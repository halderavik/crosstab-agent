import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ children, onClick, disabled }) => (
  <button onClick={onClick} disabled={disabled} data-testid="button">
    {children}
  </button>
);

interface CardProps {
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ children }) => (
  <div data-testid="card">{children}</div>
);

export const CardHeader: React.FC<CardProps> = ({ children }) => (
  <div data-testid="card-header">{children}</div>
);

export const CardContent: React.FC<CardProps> = ({ children }) => (
  <div data-testid="card-content">{children}</div>
);

export const CardTitle: React.FC<CardProps> = ({ children }) => (
  <div data-testid="card-title">{children}</div>
);

interface TabsProps extends CardProps {
  defaultValue?: string;
}

export const Tabs: React.FC<TabsProps> = ({ children, defaultValue }) => (
  <div data-testid="tabs" data-default-value={defaultValue}>{children}</div>
);

export const TabsList: React.FC<CardProps> = ({ children }) => (
  <div data-testid="tabs-list">{children}</div>
);

interface TabsTriggerProps extends CardProps {
  value: string;
}

export const TabsTrigger: React.FC<TabsTriggerProps> = ({ children, value }) => (
  <button data-testid="tabs-trigger" data-value={value}>{children}</button>
);

export const TabsContent: React.FC<TabsTriggerProps> = ({ children, value }) => (
  <div data-testid="tabs-content" data-value={value}>{children}</div>
); 