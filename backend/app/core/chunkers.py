from llama_index.core.node_parser import (
    SentenceSplitter,
    SentenceWindowNodeParser,
    HierarchicalNodeParser,
    get_leaf_nodes,
)


def get_chunker(strategy: str):
    if strategy == 'fixed':
        return SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50,
        )
    elif strategy == 'sentence_window':
        return SentenceWindowNodeParser.from_defaults(
            window_size=3,
            window_metadata_key='window',
            original_text_metadata_key='original_text',
        )
    elif strategy == 'hierarchical':
        return HierarchicalNodeParser.from_defaults(
            chunk_sizes=[2048, 512, 128],  # parent → mid → leaf
        )
    raise ValueError(f'Unknown strategy: {strategy}')


def get_nodes(documents, strategy: str):
    chunker = get_chunker(strategy)
    nodes = chunker.get_nodes_from_documents(documents)
    if strategy == 'hierarchical':
        return get_leaf_nodes(nodes)  # index only leaf nodes
    return nodes
