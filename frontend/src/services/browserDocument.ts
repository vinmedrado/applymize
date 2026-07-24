const MAX_FILE_SIZE = 8 * 1024 * 1024;

function normalizeExtractedText(text: string) {
  return text
    .replace(/\r/g, "\n")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

async function readPdf(file: File) {
  const [pdfjs, workerModule] = await Promise.all([
    import("pdfjs-dist"),
    import("pdfjs-dist/build/pdf.worker.min.mjs?url"),
  ]);
  pdfjs.GlobalWorkerOptions.workerSrc = workerModule.default;

  const loadingTask = pdfjs.getDocument({ data: await file.arrayBuffer() });
  const document = await loadingTask.promise;
  const pages: string[] = [];

  for (let pageNumber = 1; pageNumber <= document.numPages; pageNumber += 1) {
    const page = await document.getPage(pageNumber);
    const content = await page.getTextContent();
    const text = content.items
      .map((item) => ("str" in item ? item.str : ""))
      .filter(Boolean)
      .join(" ");
    pages.push(text);
  }

  return pages.join("\n\n");
}

async function readDocx(file: File) {
  const mammothModule = await import("mammoth");
  const result = await mammothModule.default.extractRawText({
    arrayBuffer: await file.arrayBuffer(),
  });
  return result.value;
}

export async function readDocumentFile(file: File): Promise<string> {
  if (file.size > MAX_FILE_SIZE) {
    throw new Error("O arquivo deve ter no máximo 8 MB.");
  }

  const extension = file.name.toLowerCase().split(".").pop();
  let text = "";

  if (extension === "pdf" || file.type === "application/pdf") {
    text = await readPdf(file);
  } else if (
    extension === "docx"
    || file.type === "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ) {
    text = await readDocx(file);
  } else if (extension === "txt" || file.type.startsWith("text/")) {
    text = await file.text();
  } else {
    throw new Error("Formato não suportado. Use PDF, DOCX ou TXT.");
  }

  const normalized = normalizeExtractedText(text);
  if (normalized.length < 80) {
    throw new Error("Não foi possível extrair texto suficiente. Tente outro arquivo ou cole o conteúdo.");
  }
  return normalized;
}
