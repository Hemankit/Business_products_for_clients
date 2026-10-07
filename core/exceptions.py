class ClientConfigError(Exception):
    pass


class MappingError(Exception):
    pass


class ProviderError(Exception):
    pass


class IntegrationError(Exception):
    pass


class LLMExtractionError(Exception):
    pass

class EmbeddingError(Exception):
    pass

class VectorStoreError(Exception):
    pass

class IngestionError(Exception):
    pass

class LLMGenerationError(Exception):
    pass

class DocumentUnderstandingError(Exception):
    pass