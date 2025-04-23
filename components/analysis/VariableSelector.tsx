"use client";

import { useState } from "react";
import { Check, ChevronsUpDown } from "lucide-react";
import { Button } from "../../components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "../../components/ui/command";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "../../components/ui/popover";
import { cn } from "../../lib/utils";

export interface Variable {
  id: string;
  name: string;
  label: string;
  type: "numeric" | "categorical" | "string";
}

interface VariableSelectorProps {
  variables: Variable[];
  selectedVariables: string[];
  onSelectionChange: (selected: string[]) => void;
  placeholder?: string;
  maxSelection?: number;
  testId?: string;
}

export function VariableSelector({
  variables,
  selectedVariables,
  onSelectionChange,
  placeholder = "Select variables...",
  maxSelection,
  testId,
}: VariableSelectorProps) {
  const [open, setOpen] = useState(false);

  const handleSelect = (variableId: string) => {
    const newSelection = selectedVariables.includes(variableId)
      ? selectedVariables.filter((id) => id !== variableId)
      : maxSelection && selectedVariables.length >= maxSelection
      ? [...selectedVariables.slice(1), variableId]
      : [...selectedVariables, variableId];

    onSelectionChange(newSelection);
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className="w-full justify-between"
          data-testid={testId}
        >
          {selectedVariables.length > 0
            ? `${selectedVariables.length} variables selected`
            : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-full p-0">
        <Command>
          <CommandInput placeholder="Search variables..." />
          <CommandEmpty>No variables found.</CommandEmpty>
          <CommandGroup>
            {variables.map((variable) => (
              <CommandItem
                key={variable.id}
                value={variable.id}
                onSelect={() => handleSelect(variable.id)}
              >
                <Check
                  className={cn(
                    "mr-2 h-4 w-4",
                    selectedVariables.includes(variable.id)
                      ? "opacity-100"
                      : "opacity-0"
                  )}
                />
                <div className="flex flex-col">
                  <span className="font-medium">{variable.name}</span>
                  <span className="text-xs text-muted-foreground">
                    {variable.label}
                  </span>
                </div>
              </CommandItem>
            ))}
          </CommandGroup>
        </Command>
      </PopoverContent>
    </Popover>
  );
} 