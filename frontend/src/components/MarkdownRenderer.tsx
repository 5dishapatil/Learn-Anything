import React, { useMemo } from 'react';
import { marked } from 'marked';
import katex from 'katex';
import DOMPurify from 'dompurify';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({
  content,
  className = '',
}) => {
  const html = useMemo(() => {
    if (!content) return '';

    let text = String(content);

    // 1. Normalize LaTeX brackets \[ ... \] and \( ... \)
    text = text.replace(/\\\[([\s\S]+?)\\\]/g, '$$$$$1$$$$');
    text = text.replace(/\\\(([\s\S]+?)\\\)/g, '$$$1$$');

    // 2. Pre-normalize headings and separators that may be compacted by LLM output
    text = text.replace(/([^\n])\s*---\s*([^\n])/g, '$1\n\n---\n\n$2');
    // Ensure headings like 'sentence. ## Heading' get split onto a new line
    text = text.replace(/([^\n])\s*(#{1,6}\s+[^\n]+)/g, '$1\n\n$2\n\n');

    const placeholders: string[] = [];

    // 3. Extract block math $$...$$
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (_, mathCode) => {
      try {
        const rendered = katex.renderToString(mathCode.trim(), {
          displayMode: true,
          throwOnError: false,
        });
        const token = `%%KATEX_BLOCK_${placeholders.length}%%`;
        placeholders.push(
          `<div class="katex-display my-4 overflow-x-auto text-center py-2.5 text-indigo-200">${rendered}</div>`
        );
        return `\n\n${token}\n\n`;
      } catch {
        return `$$\n${mathCode}\n$$`;
      }
    });

    // 4. Extract inline math $...$
    text = text.replace(/(?<!\$)\$([^\$\n]+?)\$(?!\$)/g, (_, mathCode) => {
      if (!mathCode.trim()) return `$${mathCode}$`;
      try {
        const rendered = katex.renderToString(mathCode.trim(), {
          displayMode: false,
          throwOnError: false,
        });
        const token = `%%KATEX_INLINE_${placeholders.length}%%`;
        placeholders.push(
          `<span class="katex-inline text-indigo-300 font-serif px-0.5">${rendered}</span>`
        );
        return token;
      } catch {
        return `$${mathCode}$`;
      }
    });

    // 5. Parse Markdown with marked
    marked.setOptions({
      gfm: true,
      breaks: true,
    });
    let parsed = marked.parse(text) as string;

    // 6. Restore KaTeX HTML placeholders
    placeholders.forEach((h, i) => {
      parsed = parsed.replace(new RegExp(`%%KATEX_BLOCK_${i}%%`, 'g'), h);
      parsed = parsed.replace(new RegExp(`%%KATEX_INLINE_${i}%%`, 'g'), h);
    });

    // 7. Sanitize output HTML using DOMPurify with MathML and SVG tag whitelisting
    return DOMPurify.sanitize(parsed, {
      ADD_TAGS: [
        'svg', 'path', 'g', 'rect', 'circle', 'text', 'line', 'polygon', 'foreignObject', 'style',
        'annotation', 'semantics', 'mrow', 'mi', 'mn', 'mo', 'msup', 'msub', 'mfrac', 'mover',
        'munder', 'msqrt', 'mroot', 'mtable', 'mtr', 'mtd', 'span', 'div'
      ],
      ADD_ATTR: [
        'viewBox', 'xmlns', 'fill', 'stroke', 'd', 'x', 'y', 'width', 'height', 'transform',
        'class', 'style', 'aria-hidden', 'encoding'
      ],
    });
  }, [content]);

  return (
    <div
      className={`markdown-body ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
