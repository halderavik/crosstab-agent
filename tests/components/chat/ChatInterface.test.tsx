import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { ChatInterface } from '../../../components/chat/ChatInterface';

// Mock the ChatMessage component
jest.mock('../../../components/chat/ChatMessage', () => ({
  ChatMessage: ({ message }: { message: any }) => <div data-testid="chat-message">{message.content}</div>,
}));

describe('ChatInterface Component', () => {
  const mockMessages = [
    { 
      id: '1', 
      content: 'Hello', 
      role: 'user' as const,
      timestamp: new Date()
    },
    { 
      id: '2', 
      content: 'Hi there!', 
      role: 'assistant' as const,
      timestamp: new Date()
    },
  ];

  const mockOnSendMessage = jest.fn().mockResolvedValue(undefined);

  beforeEach(() => {
    mockOnSendMessage.mockClear();
  });

  it('renders with initial messages', () => {
    render(<ChatInterface onSendMessage={mockOnSendMessage} initialMessages={mockMessages} />);
    expect(screen.getAllByTestId('chat-message')).toHaveLength(2);
  });

  it('handles message submission', async () => {
    render(<ChatInterface onSendMessage={mockOnSendMessage} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    await act(async () => {
      fireEvent.change(input, { target: { value: 'New message' } });
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(mockOnSendMessage).toHaveBeenCalledWith('New message');
    });
  });

  it('clears input after message submission', async () => {
    render(<ChatInterface onSendMessage={mockOnSendMessage} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    await act(async () => {
      fireEvent.change(input, { target: { value: 'New message' } });
      fireEvent.click(sendButton);
    });

    await waitFor(() => {
      expect(input).toHaveValue('');
    });
  });

  it('disables send button when input is empty', () => {
    render(<ChatInterface onSendMessage={mockOnSendMessage} />);
    const sendButton = screen.getByRole('button', { name: /send message/i });
    expect(sendButton).toBeDisabled();
  });

  it('enables send button when input has content', async () => {
    render(<ChatInterface onSendMessage={mockOnSendMessage} />);
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    await act(async () => {
      fireEvent.change(input, { target: { value: 'New message' } });
    });

    expect(sendButton).not.toBeDisabled();
  });

  it('shows loading state during message sending', async () => {
    const slowMock = jest.fn().mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    render(<ChatInterface onSendMessage={slowMock} />);
    
    const input = screen.getByPlaceholderText(/type your message/i);
    const sendButton = screen.getByRole('button', { name: /send message/i });

    await act(async () => {
      fireEvent.change(input, { target: { value: 'New message' } });
      fireEvent.click(sendButton);
    });

    expect(screen.getByRole('button', { name: /send message/i })).toBeDisabled();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });
  });
}); 