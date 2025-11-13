"""
News ranking service (M01A).

Uses LLM (via router) to rank articles by viral potential.
"""
from agents.checks.router import should_offload, offload_to_gemini, route_request  # noqa: F401 guardrails

import json
import re
from typing import List, Dict, Optional
from sqlmodel import Session, select

from .models import Article, RankingScore


class NewsRankingService:
    """Service for ranking articles using AI."""

    def __init__(self, db: Session):
        self.db = db

    def rank_articles(
        self,
        article_ids: List[int],
        force_rerank: bool = False
    ) -> Dict[int, RankingScore]:
        """
        Rank articles by viral potential using LLM.

        Args:
            article_ids: List of article IDs to rank
            force_rerank: If True, re-rank even if already ranked

        Returns:
            Dict mapping article_id to RankingScore
        """
        results = {}
        errors = []

        for article_id in article_ids:
            try:
                # Get article
                article = self.db.get(Article, article_id)
                if not article:
                    errors.append(f"Article {article_id} not found")
                    continue

                # Skip if already ranked (unless force_rerank)
                if not force_rerank and article.status == "ranked":
                    stmt = (
                        select(RankingScore)
                        .where(RankingScore.article_id == article_id)
                        .order_by(RankingScore.ranked_at.desc())
                        .limit(1)
                    )
                    existing_score = self.db.exec(stmt).first()
                    if existing_score:
                        results[article_id] = existing_score
                        continue

                # Rank the article
                score = self._rank_single_article(article)
                if score:
                    results[article_id] = score

                    # Update article status
                    article.status = "ranked"
                    self.db.add(article)
                    self.db.commit()

            except Exception as e:
                errors.append(f"Error ranking article {article_id}: {str(e)}")
                print(f"[Ranking] Error: {e}")
                continue

        return results

    def _rank_single_article(self, article: Article) -> Optional[RankingScore]:
        """
        Rank a single article using LLM via router.

        Args:
            article: Article to rank

        Returns:
            RankingScore if successful, None otherwise
        """
        # Build ranking prompt
        prompt = self._build_ranking_prompt(article)

        # Call LLM via router
        try:
            response = route_request(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for more consistent scoring
                max_tokens=500
            )

            if response.get("error"):
                print(f"[Ranking] LLM error: {response.get('content')}")
                return None

            # Parse response
            score_data = self._parse_ranking_response(response.get("content", ""))

            # Create ranking score record
            ranking_score = RankingScore(
                article_id=article.id,
                score=score_data["score"],
                reasoning=score_data["reasoning"],
                category=score_data["category"],
                model_used=response.get("model", "gemini-1.5-flash")
            )

            self.db.add(ranking_score)
            self.db.commit()
            self.db.refresh(ranking_score)

            return ranking_score

        except Exception as e:
            print(f"[Ranking] Error in _rank_single_article: {e}")
            return None

    def _build_ranking_prompt(self, article: Article) -> str:
        """
        Build a prompt for ranking an article.

        The prompt asks the LLM to evaluate viral potential based on:
        - Recency and timeliness
        - Visual appeal potential
        - Emotional impact
        - Clarity and shareability
        """
        prompt = f"""You are an expert content strategist evaluating news articles for viral potential on social media.

Analyze this article and provide a viral potential score from 0.0 to 1.0, where:
- 0.0-0.3 = Low potential (boring, unclear, or not timely)
- 0.4-0.6 = Medium potential (interesting but limited appeal)
- 0.7-0.8 = High potential (strong viral characteristics)
- 0.9-1.0 = Exceptional potential (extremely likely to go viral)

Article Details:
Title: {article.title}
Description: {article.description or "N/A"}
Published: {article.published_at.isoformat()}
Source: {article.source_name}

Evaluation Criteria:
1. Timeliness: Is this breaking or trending news?
2. Visual Potential: Can this be made into compelling short-form video?
3. Emotional Impact: Does it evoke strong emotions (surprise, joy, anger, curiosity)?
4. Clarity: Is the story clear and easy to understand quickly?
5. Shareability: Would people want to share this?

Respond ONLY with valid JSON in this format:
{{
  "score": 0.X,
  "reasoning": "Brief explanation of the score",
  "category": "tech" or "business" or "politics" or "entertainment" or "sports" or "other"
}}

JSON Response:"""

        return prompt

    def _parse_ranking_response(self, response_text: str) -> Dict[str, any]:
        """
        Parse LLM response to extract score, reasoning, and category.

        Tries JSON first, falls back to regex extraction if JSON parsing fails.

        Args:
            response_text: Raw LLM response

        Returns:
            Dict with score, reasoning, category
        """
        # Try JSON parsing first
        try:
            # Extract JSON from response (handle markdown code blocks)
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                else:
                    raise ValueError("No JSON found in response")

            data = json.loads(json_str)

            score = float(data.get("score", 0.5))
            score = max(0.0, min(1.0, score))  # Clamp to 0-1

            return {
                "score": score,
                "reasoning": data.get("reasoning", "No reasoning provided"),
                "category": data.get("category", "other")
            }

        except Exception as e:
            print(f"[Ranking] JSON parse failed: {e}, falling back to regex")

            # Fallback: regex extraction
            score = 0.5  # Default neutral score
            score_match = re.search(r'"score":\s*([0-9.]+)', response_text)
            if score_match:
                score = float(score_match.group(1))
                score = max(0.0, min(1.0, score))

            reasoning_match = re.search(r'"reasoning":\s*"([^"]+)"', response_text)
            reasoning = reasoning_match.group(1) if reasoning_match else "Unable to parse reasoning"

            category_match = re.search(r'"category":\s*"([^"]+)"', response_text)
            category = category_match.group(1) if category_match else "other"

            return {
                "score": score,
                "reasoning": reasoning,
                "category": category
            }

    def get_top_ranked_articles(
        self,
        limit: int = 10,
        min_score: float = 0.6
    ) -> List[tuple[Article, RankingScore]]:
        """
        Get top-ranked articles ready for script generation.

        Args:
            limit: Max number of articles to return
            min_score: Minimum score threshold

        Returns:
            List of (Article, RankingScore) tuples
        """
        # Get all ranking scores above threshold, ordered by score
        stmt = (
            select(RankingScore)
            .where(RankingScore.score >= min_score)
            .order_by(RankingScore.score.desc(), RankingScore.ranked_at.desc())
            .limit(limit)
        )
        scores = list(self.db.exec(stmt).all())

        # Get corresponding articles
        results = []
        for score in scores:
            article = self.db.get(Article, score.article_id)
            if article:
                results.append((article, score))

        return results

    def get_latest_score_for_article(self, article_id: int) -> Optional[RankingScore]:
        """Get the most recent ranking score for an article."""
        stmt = (
            select(RankingScore)
            .where(RankingScore.article_id == article_id)
            .order_by(RankingScore.ranked_at.desc())
            .limit(1)
        )
        return self.db.exec(stmt).first()
