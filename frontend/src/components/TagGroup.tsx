interface TagGroupProps {
  title: string;
  tags: string[];
  selected: string | string[] | null;
  onTagSelect: (tag: string) => void;
  exclusive: boolean;
}

export default function TagGroup({ title, tags, selected, onTagSelect, exclusive }: TagGroupProps) {
  const isSelected = (tag: string): boolean => {
    if (Array.isArray(selected)) {
      return selected.includes(tag);
    }
    return selected === tag;
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">{title}</h3>
      <div className="flex flex-wrap gap-2">
        {tags.map((tag) => (
          <button
            key={tag}
            onClick={() => onTagSelect(tag)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-150 ${
              isSelected(tag)
                ? 'bg-purple-600 text-white shadow-md transform scale-105'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
            }`}
          >
            {tag.replace('_', ' ')}
          </button>
        ))}
      </div>
    </div>
  );
}



