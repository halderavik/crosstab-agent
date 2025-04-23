import React, { act } from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CrosstabBuilder } from '../../../components/analysis/CrosstabBuilder';
import { Variable } from '../../../components/analysis/VariableSelector';

// Mock the useLoading hook
jest.mock('../../../lib/hooks/useLoading', () => ({
  useLoading: () => ({
    isLoading: false,
    withLoading: (fn: () => Promise<void>) => Promise.resolve(fn()),
  }),
}));

// Mock the VariableSelector component
jest.mock('../../../components/analysis/VariableSelector', () => ({
  VariableSelector: ({ 
    onSelectionChange, 
    selectedVariables, 
    variables, 
    testId 
  }: { 
    onSelectionChange: (selected: string[]) => void;
    selectedVariables: string[];
    variables: Variable[];
    testId?: string;
  }) => (
    <select
      data-testid={testId}
      value={selectedVariables[0] || ''}
      onChange={(e) => onSelectionChange([e.target.value])}
    >
      {variables.map((v: Variable) => (
        <option key={v.id} value={v.id}>
          {v.name}
        </option>
      ))}
    </select>
  ),
}));

// Mock UI components
jest.mock('../../../components/ui/button', () => ({
  Button: ({ children, onClick, disabled }: any) => (
    <button onClick={onClick} disabled={disabled} data-testid="button">
      {children}
    </button>
  ),
}));

jest.mock('../../../components/ui/card', () => ({
  Card: ({ children }: any) => <div data-testid="card">{children}</div>,
  CardHeader: ({ children }: any) => <div data-testid="card-header">{children}</div>,
  CardContent: ({ children }: any) => <div data-testid="card-content">{children}</div>,
  CardTitle: ({ children }: any) => <div data-testid="card-title">{children}</div>,
}));

jest.mock('../../../components/ui/tabs', () => ({
  Tabs: ({ children, defaultValue }: any) => (
    <div data-testid="tabs" data-default-value={defaultValue}>{children}</div>
  ),
  TabsList: ({ children }: any) => <div data-testid="tabs-list">{children}</div>,
  TabsTrigger: ({ children, value }: any) => (
    <button data-testid="tabs-trigger" data-value={value}>{children}</button>
  ),
  TabsContent: ({ children, value }: any) => (
    <div data-testid="tabs-content" data-value={value}>{children}</div>
  ),
}));

describe('CrosstabBuilder Component', () => {
  const mockVariables = [
    { id: '1', name: 'Age', label: 'Age', type: 'numeric' as const },
    { id: '2', name: 'Gender', label: 'Gender', type: 'categorical' as const },
    { id: '3', name: 'Income', label: 'Income', type: 'numeric' as const },
  ];

  const mockOnAnalysis = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    mockOnAnalysis.mockClear();
  });

  it('renders with initial state', () => {
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={mockOnAnalysis} />);
    
    // Check for main elements
    expect(screen.getByText('Cross-tabulation Analysis')).toBeInTheDocument();
    expect(screen.getByText('Row Variables')).toBeInTheDocument();
    expect(screen.getByText('Column Variables')).toBeInTheDocument();
    expect(screen.getByText('Table View')).toBeInTheDocument();
    expect(screen.getByText('Chart View')).toBeInTheDocument();
    expect(screen.getByText('Run Analysis')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /run analysis/i })).toBeDisabled();
  });

  it('handles variable selection for rows and columns', async () => {
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={mockOnAnalysis} />);
    
    const rowSelector = screen.getByTestId('row-selector');
    const columnSelector = screen.getByTestId('column-selector');

    // Select row variables
    await act(async () => {
      fireEvent.change(rowSelector, {
        target: { value: '1' }
      });
    });

    // Select column variables
    await act(async () => {
      fireEvent.change(columnSelector, {
        target: { value: '2' }
      });
    });

    // Verify selections through the VariableSelector's onSelectionChange
    expect(rowSelector).toHaveValue('1');
    expect(columnSelector).toHaveValue('2');
  });

  it('enables analysis button when both row and column variables are selected', async () => {
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={mockOnAnalysis} />);
    
    const rowSelector = screen.getByTestId('row-selector');
    const columnSelector = screen.getByTestId('column-selector');
    const analyzeButton = screen.getByText('Run Analysis');

    // Initially disabled
    expect(analyzeButton).toBeDisabled();

    // Select row variables
    await act(async () => {
      fireEvent.change(rowSelector, {
        target: { value: '1' }
      });
    });

    // Still disabled (no column variables)
    expect(analyzeButton).toBeDisabled();

    // Select column variables
    await act(async () => {
      fireEvent.change(columnSelector, {
        target: { value: '2' }
      });
    });

    // Now enabled
    expect(analyzeButton).not.toBeDisabled();
  });

  it('calls onAnalysis with selected variables', async () => {
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={mockOnAnalysis} />);
    
    const rowSelector = screen.getByTestId('row-selector');
    const columnSelector = screen.getByTestId('column-selector');
    const analyzeButton = screen.getByText('Run Analysis');

    // Select variables
    await act(async () => {
      fireEvent.change(rowSelector, {
        target: { value: '1' }
      });
    });

    await act(async () => {
      fireEvent.change(columnSelector, {
        target: { value: '2' }
      });
    });

    // Click analyze button
    await act(async () => {
      fireEvent.click(analyzeButton);
    });

    // Verify onAnalysis was called with correct variables
    expect(mockOnAnalysis).toHaveBeenCalledWith(['1'], ['2']);
  });

  it('shows loading state during analysis', async () => {
    // Override the useLoading mock for this test
    const mockWithLoading = jest.fn().mockImplementation((fn) => fn());
    jest.spyOn(require('../../../lib/hooks/useLoading'), 'useLoading').mockImplementation(() => ({
      isLoading: true,
      withLoading: mockWithLoading,
    }));

    const slowMock = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={slowMock} />);
    
    const rowSelector = screen.getByTestId('row-selector');
    const columnSelector = screen.getByTestId('column-selector');
    const analyzeButton = screen.getByTestId('button');

    // Select variables
    await act(async () => {
      fireEvent.change(rowSelector, {
        target: { value: '1' }
      });
    });

    await act(async () => {
      fireEvent.change(columnSelector, {
        target: { value: '2' }
      });
    });

    // Start analysis
    await act(async () => {
      fireEvent.click(analyzeButton);
    });

    // Check loading state
    expect(analyzeButton).toBeDisabled();
    expect(analyzeButton).toHaveTextContent('Analyzing...');

    // Wait for analysis to complete
    await act(async () => {
      await slowMock();
    });

    // Restore the original mock
    jest.restoreAllMocks();
  });

  it('switches between table and chart views', async () => {
    render(<CrosstabBuilder variables={mockVariables} onAnalysis={mockOnAnalysis} />);
    
    const tableTab = screen.getByText('Table View');
    const chartTab = screen.getByText('Chart View');

    // Initially on table view
    expect(tableTab).toHaveAttribute('data-value', 'table');
    expect(chartTab).toHaveAttribute('data-value', 'chart');

    // Switch to chart view
    await act(async () => {
      fireEvent.click(chartTab);
    });

    // Verify switch
    const tabsContent = screen.getAllByTestId('tabs-content');
    expect(tabsContent[1]).toHaveAttribute('data-value', 'chart');
  });
}); 