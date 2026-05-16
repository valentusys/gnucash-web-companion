# Add book switcher UI for future multi-book support

Labels: `enhancement, multi-book`

Milestone: `post-MVP multi-book`

## Goal
Add UI foundation for selecting among multiple independent GnuCash books.

## Non-goal
Do not implement collaborative editing of one book.

## Requirements
- Show available books from app metadata DB.
- Only show books accessible to current user.
- Persist selected book in route or server-side session.
- Keep default-book alias working.
