# Development Notes

## Project Overview
This is a backend take-home assignment for finding PubMed papers with industry authors.

## Implementation Decisions

### Architecture
- Chose modular design to separate concerns
- Used dataclasses for clean data structures
- Implemented scoring algorithm for author classification

### Libraries Chosen
- **Typer**: Clean CLI interface, better than argparse for this use case
- **Rich**: Nice progress bars and formatting for user experience
- **Pandas**: Easy CSV export and data manipulation
- **lxml**: Fast XML parsing for PubMed responses

### Author Classification Algorithm
The trickiest part was identifying "non-academic" authors. Implemented a scoring system based on:
1. Email domain analysis (.edu vs .com)
2. Affiliation keyword matching
3. Known company name detection

Tuned the threshold to balance precision vs recall.

## Testing Strategy
- Unit tests for each module
- Integration tests for CLI
- Manual testing with various queries

## Known Issues / Future Improvements
- Could add more sophisticated NLP for affiliation parsing
- Rate limiting could be more intelligent
- Could cache API responses for development

## Time Spent
- Initial research and planning: 2 hours
- Core implementation: 6 hours
- Testing and refinement: 2 hours
- Documentation: 1 hour

Total: ~11 hours
