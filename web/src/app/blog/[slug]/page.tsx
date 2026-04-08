import type { Metadata } from "next";
import Link from "next/link";
import { Search, ArrowLeft, Clock, ArrowRight, Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Footer } from "@/components/footer";
import { BLOG_POSTS, getBlogPostBySlug } from "@/lib/blog";
import { notFound } from "next/navigation";

export function generateStaticParams() {
  return BLOG_POSTS.map((p) => ({ slug: p.slug }));
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = getBlogPostBySlug(slug);
  if (!post) return {};
  return {
    title: post.title,
    description: post.description,
    keywords: post.tags,
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      locale: "ru_RU",
      siteName: "ГосПоиск",
    },
  };
}

export default async function BlogPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = getBlogPostBySlug(slug);
  if (!post) notFound();

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950">
      <header className="sticky top-0 z-50 border-b border-zinc-100/80 bg-white/70 backdrop-blur-xl dark:border-zinc-800/80 dark:bg-zinc-950/70">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-6 py-3">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-zinc-800 to-zinc-950 shadow-sm">
              <Search className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold tracking-tight text-zinc-900 dark:text-white">ГосПоиск</span>
          </Link>
          <Link href="/blog">
            <Button variant="outline" size="sm" className="gap-1.5 rounded-full">
              <ArrowLeft className="h-3.5 w-3.5" />
              Все статьи
            </Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-2xl px-4 py-10 sm:px-6 sm:py-16">
        {/* Meta */}
        <div className="mb-3 flex flex-wrap items-center gap-2">
          {post.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-zinc-100 px-2.5 py-0.5 text-[10px] font-medium uppercase tracking-wider text-zinc-500 dark:bg-zinc-800 dark:text-zinc-400"
            >
              {tag}
            </span>
          ))}
        </div>
        <h1 className="mb-4 text-2xl font-bold leading-tight text-zinc-900 dark:text-white sm:text-3xl">{post.title}</h1>
        <div className="mb-8 flex items-center gap-3 text-xs text-zinc-400">
          <span>{new Date(post.date).toLocaleDateString("ru-RU", { day: "numeric", month: "long", year: "numeric" })}</span>
          <span className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {post.readTime}
          </span>
        </div>

        {/* Content */}
        <article className="space-y-4">
          {post.content.map((section, i) => {
            switch (section.type) {
              case "h2":
                return (
                  <h2 key={i} className="mt-8 text-lg font-bold text-zinc-900 dark:text-white">
                    {section.text}
                  </h2>
                );
              case "h3":
                return (
                  <h3 key={i} className="mt-5 text-base font-semibold text-zinc-800 dark:text-zinc-200">
                    {section.text}
                  </h3>
                );
              case "p":
                return (
                  <p key={i} className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                    {section.text}
                  </p>
                );
              case "ul":
                return (
                  <ul key={i} className="ml-4 list-disc space-y-1.5">
                    {section.items?.map((item, j) => (
                      <li key={j} className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                        {item}
                      </li>
                    ))}
                  </ul>
                );
              case "ol":
                return (
                  <ol key={i} className="ml-4 list-decimal space-y-1.5">
                    {section.items?.map((item, j) => (
                      <li key={j} className="text-sm leading-relaxed text-zinc-600 dark:text-zinc-400">
                        {item}
                      </li>
                    ))}
                  </ol>
                );
              case "tip":
                return (
                  <div key={i} className="flex gap-3 rounded-xl bg-amber-50 p-4 dark:bg-amber-950/30">
                    <Lightbulb className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
                    <p className="text-sm leading-relaxed text-amber-800 dark:text-amber-300">{section.text}</p>
                  </div>
                );
              case "cta":
                return (
                  <div key={i} className="mt-8 rounded-2xl bg-zinc-900 p-6 text-center sm:p-8">
                    <p className="mb-4 text-sm text-zinc-300">{section.text}</p>
                    <Link href="/dashboard">
                      <Button className="gap-2 rounded-xl bg-white px-6 text-zinc-900 hover:bg-zinc-100">
                        <Search className="h-4 w-4" />
                        Попробовать бесплатно
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    </Link>
                  </div>
                );
              default:
                return null;
            }
          })}
        </article>

        {/* Related posts */}
        <div className="mt-14 border-t border-zinc-100 pt-10 dark:border-zinc-800">
          <h3 className="mb-5 text-sm font-semibold uppercase tracking-wider text-zinc-400">
            Другие статьи
          </h3>
          <div className="space-y-3">
            {BLOG_POSTS.filter((p) => p.slug !== post.slug)
              .slice(0, 3)
              .map((p) => (
                <Link
                  key={p.slug}
                  href={`/blog/${p.slug}`}
                  className="group block rounded-xl border border-zinc-100 p-4 transition-all hover:border-zinc-200 hover:shadow-sm dark:border-zinc-800 dark:hover:border-zinc-700"
                >
                  <h4 className="text-sm font-semibold text-zinc-900 transition-colors group-hover:text-blue-600 dark:text-white">
                    {p.title}
                  </h4>
                  <p className="mt-1 text-xs text-zinc-400">{p.readTime}</p>
                </Link>
              ))}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
