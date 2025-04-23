# SPSS Data Analysis Application

An AI-driven application for analyzing SPSS survey data with advanced cross-tabulation capabilities and natural language query support.

## Features

### Completed Features
- **Data Processing**
  - SPSS file parsing and validation
  - Data cleaning and transformation
  - Custom variable processing
  - Support for multiple file formats (CSV, Excel)

- **Analysis Engine**
  - Cross-tabulation with banner table support
  - Statistical significance testing
  - Advanced data analysis capabilities
  - Custom variable creation and manipulation

- **Visualization Engine**
  - Interactive chart generation
  - Multiple chart types (bar, stacked bar, heatmap, line, pie)
  - Custom styling and theming
  - Export functionality
  - Support for both Matplotlib and Plotly visualizations

- **AI Integration**
  - DeepSeek-powered LLM agent
  - Natural language query processing
  - Context-aware analysis
  - Intelligent response generation

### In Progress
- Frontend interface development
- API endpoints implementation
- Testing infrastructure
- Documentation

## Tech Stack

### Backend
- Python 3.8+
- FastAPI
- LangChain
- DeepSeek
- Pandas
- PyReadStat
- NumPy
- SciPy
- Matplotlib
- Seaborn
- Plotly
- Kaleido (for Plotly image export)

### Frontend
- Next.js
- React
- Tailwind CSS
- shadcn/ui
- Chart.js
- React Table
- Axios

## Project Structure

```
spss_analyzer_backend/
├── api/                # API endpoints
├── config/            # Configuration files
├── core/              # Core functionality
│   ├── analysis/      # Analysis engine
│   ├── storage/       # Storage management
│   └── visualization/ # Visualization engine
├── tests/             # Test suite
└── uploads/           # File upload directory

spss-analyzer-frontend/
├── components/        # React components
├── lib/              # Utility functions
├── pages/            # Next.js pages
└── tests/            # Frontend tests
```

## Setup Instructions

### Backend Setup

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create `.env` file:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your configuration

4. Run the development server:
   ```bash
   uvicorn api.main:app --reload
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd spss-analyzer-frontend
   npm install
   ```

2. Create `.env.local` file:
   ```bash
   cp .env.example .env.local
   ```
   Edit `.env.local` with your configuration

3. Run the development server:
   ```bash
   npm run dev
   ```

## Known Issues

### Windows-Specific Issues
- **Plotly Image Export**: The kaleido package (required for Plotly image export) may have initialization issues on Windows. As a workaround:
  - Use HTML export format for Plotly visualizations
  - Use Matplotlib for static image exports
  - The issue is being tracked and will be addressed in a future update

### General Issues
- Large dataset processing may require additional memory
- Some statistical tests may be computationally intensive
- File upload size limits may need adjustment based on server configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- DeepSeek for LLM capabilities
- LangChain for AI integration
- FastAPI for backend framework
- Next.js for frontend framework 