export type StageStatus = "pending" | "processing" | "completed" | "failed" | "skipped"

export interface WorkflowStage {
    id: string
    name: string
    description: string
    status: StageStatus
    order: number
}

export interface Workflow {
    id: string
    name: string
    description: string
    stages: WorkflowStage[]
    createdAt: string
    updatedAt: string
    status: "active" | "inactive" | "draft"
}