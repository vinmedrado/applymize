function normalizeHeading(line: string) {
  return line.replace(/^#+\s*/, "").trim();
}

export function MarkdownBlock({ content }: { content: string }) {
  const lines = (content || "").split("\n");
  const blocks: Array<{ title: string; body: string[] }> = [];
  let current: { title: string; body: string[] } | null = null;

  for (const line of lines) {
    if (line.startsWith("# ")) {
      if (current) blocks.push(current);
      current = { title: normalizeHeading(line), body: [] };
    } else if (line.startsWith("## ")) {
      if (current) blocks.push(current);
      current = { title: normalizeHeading(line), body: [] };
    } else {
      if (!current) current = { title: "Conteúdo", body: [] };
      current.body.push(line);
    }
  }
  if (current) blocks.push(current);

  return (
    <div className="space-y-4">
      {blocks.map((block, index) => (
        <section key={index} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-lg font-bold text-slate-950">{block.title}</h3>
          <div className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
            {block.body.filter(Boolean).map((line, lineIndex) => {
              if (line.trim().startsWith("-")) {
                return <p key={lineIndex} className="pl-3">• {line.replace(/^[-•]\s*/, "")}</p>;
              }
              if (line.startsWith("**") && line.includes(":**")) {
                return <p key={lineIndex} className="font-medium">{line.replaceAll("**", "")}</p>;
              }
              if (line.startsWith("### ")) {
                return <h4 key={lineIndex} className="pt-2 font-bold text-slate-900">{normalizeHeading(line)}</h4>;
              }
              return <p key={lineIndex}>{line.replaceAll("**", "")}</p>;
            })}
          </div>
        </section>
      ))}
    </div>
  );
}
