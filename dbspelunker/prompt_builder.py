import re
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Literal, Optional, Self, Union

BlockKind = Literal["markdown", "code", "json", "yaml", "text"]


@dataclass
class SupportBlock:
    title: str
    body: str
    kind: BlockKind = "markdown"
    language: Optional[str] = None


@dataclass
class ExampleBlock:
    title: Optional[str]
    body: str
    kind: BlockKind = "markdown"
    language: Optional[str] = None


@dataclass
class RenderOptions:
    base_heading_level: int = 1
    include_toc: bool = False
    collapse_supporting_info: bool = False
    strict_validate: bool = True
    strip_trailing_whitespace: bool = True


@dataclass
class PromptBuilder:
    """
    Generic prompt builder that renders clean, consistently formatted Markdown.
    Use the fluent API to add content, then call .render().

    Required (by default): title
    Optional: all other sections. Empty sections are omitted in output.
    """

    title: Optional[str] = None
    instructions: List[str] = field(default_factory=list)
    rules: List[str] = field(default_factory=list)
    output_desc: Optional[str] = None
    validation: Optional[str] = None
    supporting: List[SupportBlock] = field(default_factory=list)
    examples: List[ExampleBlock] = field(default_factory=list)
    extra_sections: List[tuple[str, Union[str, Iterable[str]]]] = field(
        default_factory=list
    )
    summary: Optional[str] = None

    metadata: Dict[str, str] = field(default_factory=dict)

    def with_title(self, text: str) -> Self:
        self.title = _clean(text)
        return self

    def add_instruction(self, text: str) -> Self:
        self.instructions.append(_clean(text))
        return self

    def extend_instructions(self, items: Iterable[str]) -> Self:
        self.instructions.extend(_clean(x) for x in items)
        return self

    def add_rule(self, text: str) -> Self:
        self.rules.append(_clean(text))
        return self

    def extend_rules(self, items: Iterable[str]) -> Self:
        self.rules.extend(_clean(x) for x in items)
        return self

    def set_output(self, description: str) -> Self:
        self.output_desc = _clean(description)
        return self

    def set_validation(self, description: str) -> Self:
        self.validation = _clean(description)
        return self

    def add_supporting_info(
        self,
        title: str,
        body: str,
        *,
        kind: BlockKind = "markdown",
        language: Optional[str] = None,
    ) -> Self:
        self.supporting.append(
            SupportBlock(_clean(title), _dedent_preserve(body), kind, language)
        )
        return self

    def add_example(
        self,
        body: str,
        *,
        title: Optional[str] = None,
        kind: BlockKind = "markdown",
        language: Optional[str] = None,
    ) -> Self:
        self.examples.append(
            ExampleBlock(
                _clean(title) if title else None, _dedent_preserve(body), kind, language
            )
        )
        return self

    def add_section(self, name: str, content: Union[str, Iterable[str]]) -> Self:
        self.extra_sections.append((_clean(name), content))
        return self

    def set_summary(self, text: str) -> Self:
        self.summary = _clean(text)
        return self

    def add_metadata(self, key: str, value: str) -> Self:
        self.metadata[_clean_inline(key)] = _clean_inline(value)
        return self

    def render(self, options: Optional[RenderOptions] = None) -> str:
        opt = options or RenderOptions()
        if opt.strict_validate:
            self._validate()

        def H(level: int) -> str:
            return "#" * max(1, opt.base_heading_level + (level - 1))

        parts: List[str] = []

        if self.title:
            parts.append(f"{H(1)} {self.title}")

        if opt.include_toc:
            parts.append(self._render_toc())

        if self.instructions:
            parts.append(f"{H(2)} Instructions")
            parts.append(_bullets(self.instructions))

        if self.rules:
            parts.append(f"{H(2)} Rules")
            parts.append(_bullets(self.rules))

        if self.output_desc:
            parts.append(f"{H(2)} Output")
            parts.append(
                f"{H(4)} Return output exactly formatted specified below with NO formatting, markdown, or code blocks. Check Field Descriptions for field level details."
            )
            parts.append(self.output_desc.strip())

        if self.validation:
            parts.append(f"{H(2)} Validation")
            parts.append(self.validation.strip())

        if self.supporting:
            parts.append(f"{H(2)} Supporting information")
            for i, block in enumerate(self.supporting, 1):
                section_title = f"{H(3)} {block.title or f'Item {i}'}"
                content = _render_block(block.body, block.kind, block.language)
                if opt.collapse_supporting_info:
                    parts.append(_details(section_title, content))
                else:
                    parts.append(section_title)
                    parts.append(content)

        if self.examples:
            parts.append(f"{H(2)} Example")
            for idx, ex in enumerate(self.examples, 1):
                subtitle = ex.title or f"Example {idx}"
                parts.append(f"{H(3)} {subtitle}")
                parts.append(_render_block(ex.body, ex.kind, ex.language))

        for name, section_content in self.extra_sections:
            parts.append(f"{H(2)} {name}")
            if isinstance(section_content, str):
                parts.append(section_content.strip())
            else:
                parts.append(_bullets([_clean(x) for x in section_content]))

        if self.summary:
            parts.append(f"{H(2)} Summary")
            parts.append(self.summary.strip())
        else:
            parts.append(f"{H(2)} Summary")
            parts.append(self._auto_summary())

        if self.metadata:
            meta_lines = " ".join(f'{k}="{v}"' for k, v in self.metadata.items())
            parts.append(f"<!-- metadata: {meta_lines} -->")

        doc = "\n\n".join(p for p in parts if p and p.strip())

        if opt.strip_trailing_whitespace:
            doc = _strip_trailing_ws(doc)

        return doc

    def _validate(self) -> None:
        if not self.title:
            raise ValueError("PromptBuilder: title is required.")

    def _render_toc(self) -> str:
        sections = []
        if self.instructions:
            sections.append("Instructions")
        if self.rules:
            sections.append("Rules")
        if self.output_desc:
            sections.append("Output")
        if self.validation:
            sections.append("Validation")
        if self.supporting:
            sections.append("Supporting information")
        if self.examples:
            sections.append("Example")
        for name, _ in self.extra_sections:
            sections.append(name)
        sections.append("Summary")

        lines = ["## Table of contents"]
        for s in sections:
            slug = _slug(s)
            lines.append(f"- [{s}](#{slug})")
        return "\n".join(lines)

    def _auto_summary(self) -> str:
        parts = []
        if self.title:
            parts.append(f"- **Directive:** {self.title}")
        if self.instructions:
            parts.append(f"- **Instructions:** {len(self.instructions)} bullet(s)")
        if self.rules:
            parts.append(f"- **Rules:** {len(self.rules)} constraint(s)")
        if self.output_desc:
            parts.append("- **Output:** defined")
        if self.validation:
            parts.append("- **Validation:** defined")
        if self.supporting:
            parts.append(f"- **Supporting info:** {len(self.supporting)} block(s)")
        if self.examples:
            parts.append(f"- **Examples:** {len(self.examples)} block(s)")
        if self.extra_sections:
            parts.append(f"- **Custom sections:** {len(self.extra_sections)}")
        if not parts:
            return "This prompt has no substantive content yet."
        return "\n".join(parts)


line_re = re.compile(r"\s+\n")
many_space_re = re.compile(r"\s+")
not_word_re = re.compile(r"[^\w\s-]")
empty_space_re = re.compile(r"[\s_]+")


def _clean(text: str) -> str:
    return line_re.sub("\n", text.strip())


def _clean_inline(text: str) -> str:
    return many_space_re.sub(" ", text.strip())


def _dedent_preserve(text: str) -> str:
    return textwrap.dedent(text).rstrip("\n")


def _bullets(items: Iterable[str]) -> str:
    return "\n".join(f"* {line}" for line in items)


def _slug(s: str) -> str:
    s = s.strip().lower()
    s = not_word_re.sub("", s)
    s = empty_space_re.sub("-", s)
    return s


def _render_block(body: str, kind: BlockKind, language: Optional[str]) -> str:
    return body.strip()


sections_re = re.compile(r"^#+\s*")


def _details(summary_heading_md: str, content_md: str) -> str:
    plain = sections_re.sub("", summary_heading_md)
    return f"<details>\n<summary>{plain}</summary>\n\n{content_md}\n\n</details>"


def _strip_trailing_ws(md: str) -> str:
    return "\n".join(line.rstrip() for line in md.splitlines())
