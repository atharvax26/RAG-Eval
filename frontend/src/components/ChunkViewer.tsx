import type { ChunkResult } from '../types/api'

interface ChunkViewerProps {
  chunks: ChunkResult[]
  title: string
}

export default function ChunkViewer({ chunks, title }: ChunkViewerProps) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-lgray font-semibold text-sm uppercase tracking-wide">{title}</h3>
      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto scrollbar-thin pr-1">
        {chunks.map((chunk, i) => (
          <div key={chunk.chunk_id} className="bg-card2 border border-border rounded p-3 flex flex-col gap-1">
            <div className="flex justify-between items-center">
              <span className="text-mgray text-xs font-mono">chunk {i + 1}</span>
              <span className="text-teal text-xs font-mono">score: {chunk.score.toFixed(3)}</span>
            </div>
            <p className="text-lgray text-xs leading-relaxed line-clamp-4">{chunk.text}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
