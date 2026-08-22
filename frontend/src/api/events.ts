import { z } from "zod";


const citationSchema = z.object({
  chunk_id: z.string(),
  title: z.string(),
  heading: z.string(),
  url: z.string().url(),
  evidence: z.string(),
});

const claimSchema = z.object({
  text: z.string(),
  role: z.enum(["core", "supporting"]),
  citation: citationSchema,
});

export const terminalResultSchema = z.object({
  status: z.enum(["answer", "unknown", "clarification"]),
  message: z.string(),
  claims: z.array(claimSchema),
  model_calls: z.number().int().min(0).max(2),
});

export type TerminalResult = z.infer<typeof terminalResultSchema>;


export function parseTerminalEvent(stream: string): TerminalResult {
  for (const block of stream.trim().split("\n\n")) {
    const lines = block.split("\n");
    if (lines[0] === "event: request.completed") {
      const data = lines.find((line) => line.startsWith("data: "))?.slice(6);
      if (!data) throw new Error("missing_terminal_data");
      return terminalResultSchema.parse(JSON.parse(data));
    }
  }
  throw new Error("missing_terminal_event");
}
