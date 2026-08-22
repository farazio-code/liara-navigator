import { z } from "zod";

const claimSchema = z.object({
  text: z.string(),
  role: z.enum(["core", "supporting"]),
  chunk_id: z.string(),
  evidence: z.string(),
});

export const terminalResultSchema = z.object({
  status: z.enum(["answer", "unknown", "clarification"]),
  message: z.string(),
  claims: z.array(claimSchema),
  model_calls: z.number().int().min(0).max(2),
});

export type TerminalResult = z.infer<typeof terminalResultSchema>;

export function parseTerminalEvent(stream: string): TerminalResult {
  const blocks = stream.trim().split(/\r?\n\r?\n/);

  for (const block of blocks) {
    const lines = block.split(/\r?\n/);

    const eventLine = lines.find((line) =>
      line.startsWith("event:"),
    );

    if (eventLine?.trim() !== "event: request.completed") {
      continue;
    }

    const dataLine = lines.find((line) =>
      line.startsWith("data: "),
    );

    if (!dataLine) {
      throw new Error("missing_terminal_data");
    }

    const rawData = dataLine.slice("data: ".length);

    let parsed: unknown;

    try {
      parsed = JSON.parse(rawData);
    } catch {
      throw new Error("invalid_terminal_json");
    }

    return terminalResultSchema.parse(parsed);
  }

  throw new Error("missing_terminal_event");
}
