import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { VariableSelector } from '../../../components/analysis/VariableSelector';

const mockVariables = [
  { id: '1', name: 'Age', label: 'Age', type: 'numeric' as const },
  { id: '2', name: 'Gender', label: 'Gender', type: 'categorical' as const },
  { id: '3', name: 'Income', label: 'Income', type: 'numeric' as const },
];

// Mock UI components
jest.mock('../../../components/ui/button', () => ({
  Button: ({ children, onClick, ...props }: any) => (
    <button onClick={onClick} {...props} data-testid="button">
      {children}
    </button>
  ),
}));

jest.mock('../../../components/ui/command', () => ({
  Command: ({ children }: any) => <div data-testid="command">{children}</div>,
  CommandEmpty: ({ children }: any) => <div data-testid="command-empty">{children}</div>,
  CommandGroup: ({ children }: any) => <div data-testid="command-group">{children}</div>,
  CommandInput: ({ onChange, value }: any) => (
    <input
      data-testid="command-input"
      onChange={(e) => onChange?.(e.target.value)}
      value={value || ''}
    />
  ),
  CommandItem: ({ children, onSelect, value }: any) => (
    <div data-testid={`command-item-${value}`} onClick={onSelect}>
      {children}
    </div>
  ),
}));

jest.mock('../../../components/ui/popover', () => ({
  Popover: ({ children }: any) => <div data-testid="popover">{children}</div>,
  PopoverContent: ({ children }: any) => <div data-testid="popover-content">{children}</div>,
  PopoverTrigger: ({ children }: any) => <div data-testid="popover-trigger">{children}</div>,
}));

describe('VariableSelector Component', () => {
  it('renders with initial state', () => {
    const onSelectionChange = jest.fn();
    render(
      <VariableSelector
        variables={mockVariables}
        selectedVariables={[]}
        onSelectionChange={onSelectionChange}
      />
    );

    expect(screen.getByTestId('command-input')).toBeInTheDocument();
    expect(screen.getByText('Select variables...')).toBeInTheDocument();
  });

  it('handles variable selection', async () => {
    const onSelectionChange = jest.fn();
    render(
      <VariableSelector
        variables={mockVariables}
        selectedVariables={[]}
        onSelectionChange={onSelectionChange}
      />
    );

    const ageItem = screen.getByTestId('command-item-1');
    await act(async () => {
      fireEvent.click(ageItem);
    });

    expect(onSelectionChange).toHaveBeenCalledWith(['1']);
  });

  it('handles variable deselection', async () => {
    const onSelectionChange = jest.fn();
    render(
      <VariableSelector
        variables={mockVariables}
        selectedVariables={['1']}
        onSelectionChange={onSelectionChange}
      />
    );

    const ageItem = screen.getByTestId('command-item-1');
    await act(async () => {
      fireEvent.click(ageItem);
    });

    expect(onSelectionChange).toHaveBeenCalledWith([]);
  });

  it('replaces first selected item when maxSelection is reached', async () => {
    const onSelectionChange = jest.fn();
    render(
      <VariableSelector
        variables={mockVariables}
        selectedVariables={['1']}
        onSelectionChange={onSelectionChange}
        maxSelection={1}
      />
    );

    const genderItem = screen.getByTestId('command-item-2');
    await act(async () => {
      fireEvent.click(genderItem);
    });

    expect(onSelectionChange).toHaveBeenCalledWith(['2']);
  });

  it('shows selected variables count', () => {
    const onSelectionChange = jest.fn();
    render(
      <VariableSelector
        variables={mockVariables}
        selectedVariables={['1', '2']}
        onSelectionChange={onSelectionChange}
      />
    );

    expect(screen.getByText('2 variables selected')).toBeInTheDocument();
  });
}); 