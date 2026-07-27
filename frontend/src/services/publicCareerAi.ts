const STORAGE_KEY = "applymize.portfolio-ai.v1";
const MAX_QUESTION_CHARS = 500;

export type PublicCareerAIResult = {
  answer: string;
  provider: string;
  model: string;
};

export type StoredPublicCareerAIResult = PublicCareerAIResult & {
  question: string;
};

export class PublicCareerAIError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "PublicCareerAIError";
    this.status = status;
  }
}

export function loadPublicCareerAIResult(): StoredPublicCareerAIResult | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<StoredPublicCareerAIResult>;
    if (!parsed.question || !parsed.answer || !parsed.provider || !parsed.model) return null;
    return parsed as StoredPublicCareerAIResult;
  } catch {
    return null;
  }
}

function storePublicCareerAIResult(result: StoredPublicCareerAIResult) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(result));
  } catch {
    // O limite da função continua protegendo o orçamento quando o storage não está disponível.
  }
}

export async function askPublicCareerAI(question: string): Promise<PublicCareerAIResult> {
  const cleanQuestion = question.trim();
  if (!cleanQuestion || cleanQuestion.length > MAX_QUESTION_CHARS) {
    throw new PublicCareerAIError(`Escreva uma pergunta de até ${MAX_QUESTION_CHARS} caracteres.`, 400);
  }

  const response = await fetch("/api/portfolio-ai", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question: cleanQuestion }),
  });

  const data = await response.json().catch(() => null) as (Partial<PublicCareerAIResult> & { error?: string }) | null;
  if (!response.ok) {
    const rateLimitMessage = "Este acesso já utilizou o crédito de IA disponível. A resposta fica limitada a uma consulta para proteger a demonstração.";
    throw new PublicCareerAIError(
      response.status === 429 ? rateLimitMessage : data?.error || "A IA não conseguiu responder agora. Tente novamente mais tarde.",
      response.status,
    );
  }

  if (!data?.answer || !data.provider || !data.model) {
    throw new PublicCareerAIError("A IA retornou uma resposta inválida.", 502);
  }

  const result: PublicCareerAIResult = {
    answer: data.answer,
    provider: data.provider,
    model: data.model,
  };
  storePublicCareerAIResult({ question: cleanQuestion, ...result });
  return result;
}
