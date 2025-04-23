"use client";

import { useState } from "react";
import { VariableSelector } from "./VariableSelector";
import { Button } from "../ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { useLoading } from "../../lib/hooks/useLoading";

interface Variable {
  id: string;
  name: string;
  label: string;
  type: "numeric" | "categorical" | "string";
}

interface CrosstabBuilderProps {
  variables: Variable[];
  onAnalysis: (rowVars: string[], colVars: string[]) => Promise<void>;
}

export function CrosstabBuilder({ variables, onAnalysis }: CrosstabBuilderProps) {
  const [rowVariables, setRowVariables] = useState<string[]>([]);
  const [columnVariables, setColumnVariables] = useState<string[]>([]);
  const { isLoading, withLoading } = useLoading();

  const handleAnalysis = async () => {
    if (rowVariables.length === 0 || columnVariables.length === 0) {
      return;
    }

    await withLoading(onAnalysis(rowVariables, columnVariables));
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Cross-tabulation Analysis</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="text-sm font-medium">Row Variables</label>
            <VariableSelector
              variables={variables}
              selectedVariables={rowVariables}
              onSelectionChange={setRowVariables}
              placeholder="Select row variables..."
              testId="row-selector"
            />
          </div>
          <div className="space-y-2">
            <label className="text-sm font-medium">Column Variables</label>
            <VariableSelector
              variables={variables}
              selectedVariables={columnVariables}
              onSelectionChange={setColumnVariables}
              placeholder="Select column variables..."
              testId="column-selector"
            />
          </div>
        </div>

        <Tabs defaultValue="table" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="table">Table View</TabsTrigger>
            <TabsTrigger value="chart">Chart View</TabsTrigger>
          </TabsList>
          <TabsContent value="table">
            <div className="rounded-md border">
              {/* Table view will be implemented here */}
            </div>
          </TabsContent>
          <TabsContent value="chart">
            <div className="rounded-md border">
              {/* Chart view will be implemented here */}
            </div>
          </TabsContent>
        </Tabs>

        <div className="flex justify-end">
          <Button
            onClick={handleAnalysis}
            disabled={isLoading || rowVariables.length === 0 || columnVariables.length === 0}
          >
            {isLoading ? "Analyzing..." : "Run Analysis"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
} 