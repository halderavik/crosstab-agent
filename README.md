# SPSS Analyzer Frontend

A modern web application for analyzing SPSS data files, built with Next.js, TypeScript, and React.

## Features

- File upload and validation
- Cross-tabulation analysis
- Interactive data visualization
- Modern UI with dark mode support
- Responsive design

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **UI**: React, Tailwind CSS, Radix UI
- **Testing**: Jest, React Testing Library
- **Data Visualization**: Chart.js
- **State Management**: React Hooks

## Prerequisites

- Node.js 18+ 
- npm 9+

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Project Structure

```
spss-analyzer-frontend/
├── app/                    # Next.js app directory
├── components/            # React components
│   ├── analysis/         # Analysis components
│   ├── chat/            # Chat interface components
│   ├── forms/           # Form components
│   └── ui/              # Reusable UI components
├── lib/                  # Utility functions and hooks
├── tests/               # Test files
│   ├── components/      # Component tests
│   └── api/            # API route tests
└── types/              # TypeScript type definitions
```

## Testing

Run tests with:
```bash
npm test              # Run all tests
npm run test:watch    # Run tests in watch mode
npm run test:coverage # Generate test coverage report
```

## Development Guidelines

- Follow TypeScript best practices
- Write unit tests for new features
- Use React Testing Library for component tests
- Follow the project's code structure
- Document complex logic with comments

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.
