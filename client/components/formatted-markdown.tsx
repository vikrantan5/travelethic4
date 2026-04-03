import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import { Compass, MapPin, Utensils, DollarSign, Info, Star, CheckCircle } from "lucide-react";

interface FormattedMarkdownProps {
  content: string;
  type?: "destination" | "dining" | "budget" | "general";
}

export function FormattedMarkdown({ content, type = "general" }: FormattedMarkdownProps) {
  // Parse content to add better formatting
  const getIconForSection = (title: string) => {
    const lowerTitle = title.toLowerCase();
    if (lowerTitle.includes("attraction") || lowerTitle.includes("place") || lowerTitle.includes("visit")) {
      return <MapPin className="w-4 h-4 text-purple-600" />;
    } else if (lowerTitle.includes("food") || lowerTitle.includes("dining") || lowerTitle.includes("restaurant") || lowerTitle.includes("eat")) {
      return <Utensils className="w-4 h-4 text-orange-600" />;
    } else if (lowerTitle.includes("budget") || lowerTitle.includes("cost") || lowerTitle.includes("price")) {
      return <DollarSign className="w-4 h-4 text-green-600" />;
    } else if (lowerTitle.includes("tip") || lowerTitle.includes("advice")) {
      return <Info className="w-4 h-4 text-blue-600" />;
    } else if (lowerTitle.includes("best") || lowerTitle.includes("top")) {
      return <Star className="w-4 h-4 text-yellow-600" />;
    }
    return <Compass className="w-4 h-4 text-purple-600" />;
  };

  return (
    <div className="formatted-content space-y-6">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4 flex items-center gap-3 pb-3 border-b-2 border-purple-200 dark:border-purple-800" {...props}>
              {getIconForSection(String(props.children))}
              {props.children}
            </h1>
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-xl md:text-2xl font-bold text-gray-800 dark:text-gray-100 mt-8 mb-4 flex items-center gap-2 pb-2 border-b border-purple-100 dark:border-purple-900" {...props}>
              {getIconForSection(String(props.children))}
              {props.children}
            </h2>
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-lg md:text-xl font-semibold text-gray-700 dark:text-gray-200 mt-6 mb-3 flex items-center gap-2" {...props}>
              <CheckCircle className="w-4 h-4 text-purple-500" />
              {props.children}
            </h3>
          ),
          h4: ({ node, ...props }) => (
            <h4 className="text-base md:text-lg font-semibold text-gray-700 dark:text-gray-300 mt-4 mb-2" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4 text-base" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="space-y-3 mb-6 ml-2" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="space-y-3 mb-6 ml-2 list-decimal list-inside" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="flex items-start gap-3 p-3 rounded-lg bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/20 dark:to-blue-950/20 border border-purple-100 dark:border-purple-900 hover:shadow-md transition-shadow">
              <span className="flex-shrink-0 w-2 h-2 rounded-full bg-purple-500 mt-2"></span>
              <span className="flex-1 text-gray-700 dark:text-gray-300">{props.children}</span>
            </li>
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-bold text-purple-700 dark:text-purple-400" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="italic text-blue-600 dark:text-blue-400" {...props} />
          ),
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-4 border-purple-500 pl-4 py-2 my-4 bg-purple-50 dark:bg-purple-950/20 rounded-r-lg italic text-gray-700 dark:text-gray-300" {...props} />
          ),
          hr: ({ node, ...props }) => (
            <hr className="my-8 border-t-2 border-purple-200 dark:border-purple-800" {...props} />
          ),
          a: ({ node, ...props }) => (
            <a className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300 underline font-medium" target="_blank" rel="noopener noreferrer" {...props} />
          ),
          code: ({ node, inline, ...props }: any) =>
            inline ? (
              <code className="bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 px-2 py-0.5 rounded text-sm font-mono" {...props} />
            ) : (
              <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono my-4" {...props} />
            ),
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-6 rounded-lg border border-purple-200 dark:border-purple-800">
              <table className="min-w-full divide-y divide-purple-200 dark:divide-purple-800" {...props} />
            </div>
          ),
          thead: ({ node, ...props }) => (
            <thead className="bg-gradient-to-r from-purple-100 to-blue-100 dark:from-purple-900 dark:to-blue-900" {...props} />
          ),
          tbody: ({ node, ...props }) => (
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-purple-100 dark:divide-purple-900" {...props} />
          ),
          th: ({ node, ...props }) => (
            <th className="px-6 py-3 text-left text-xs font-bold text-purple-700 dark:text-purple-300 uppercase tracking-wider" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-6 py-4 text-sm text-gray-700 dark:text-gray-300" {...props} />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
