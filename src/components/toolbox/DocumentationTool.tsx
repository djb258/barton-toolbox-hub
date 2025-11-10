import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";

export const DocumentationTool = () => {
  return (
    <Tabs defaultValue="overview" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="schema">Process Schema</TabsTrigger>
        <TabsTrigger value="rules">Live Rules</TabsTrigger>
      </TabsList>

      <TabsContent value="overview" className="space-y-4">
        <ScrollArea className="h-[400px] rounded-lg border bg-card p-6">
          <div className="prose prose-sm max-w-none">
            <h2 className="text-lg font-bold mb-4">Barton Toolbox Documentation</h2>
            
            <h3 className="text-base font-semibold mt-6 mb-2">Purpose</h3>
            <p className="text-sm text-muted-foreground mb-4">
              The Barton Toolbox is a unified interface for all process management tools. 
              It provides a centralized location for routing, validation, mapping, parsing, 
              document generation, and monitoring.
            </p>

            <h3 className="text-base font-semibold mt-6 mb-2">Tool Overview</h3>
            <ul className="text-sm text-muted-foreground space-y-2">
              <li><strong>Router:</strong> Intake routing system that tags and forwards payloads</li>
              <li><strong>Validator:</strong> Executes enrichment and validation rules from Neon database</li>
              <li><strong>Mapper:</strong> Field mapping tool for transforming data to STAMPED schema</li>
              <li><strong>Parser:</strong> Document parser for extracting structured data from PDFs/Docs</li>
              <li><strong>Doc Filler:</strong> Template filling system for generating documents</li>
              <li><strong>Logger:</strong> Central audit logging and error tracking system</li>
            </ul>

            <h3 className="text-base font-semibold mt-6 mb-2">Doctrine Alignment</h3>
            <p className="text-sm text-muted-foreground mb-4">
              This toolbox follows the ORBT/STAMPED doctrine, ensuring all tools integrate 
              seamlessly with the master process schema and audit systems.
            </p>
          </div>
        </ScrollArea>
      </TabsContent>

      <TabsContent value="schema" className="space-y-4">
        <div className="rounded-lg border bg-card p-6">
          <div className="text-center text-muted-foreground">
            <p className="mb-4">Process Flow Diagram</p>
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-12">
              <p className="text-sm">Mermaid diagram would be rendered here</p>
              <p className="text-xs mt-2">Router → Validator → Mapper → Doc Filler</p>
            </div>
          </div>
        </div>
      </TabsContent>

      <TabsContent value="rules" className="space-y-4">
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-sm font-semibold mb-4">Active Validation Rules</h3>
          <div className="space-y-3">
            <div className="border-l-2 border-tool-validator pl-4">
              <div className="font-mono text-xs text-muted-foreground">VAL-001</div>
              <div className="font-medium">Email Validation</div>
              <div className="text-sm text-muted-foreground">Validates email format using regex pattern</div>
            </div>
            <div className="border-l-2 border-tool-validator pl-4">
              <div className="font-mono text-xs text-muted-foreground">VAL-002</div>
              <div className="font-medium">Amount Range Check</div>
              <div className="text-sm text-muted-foreground">Ensures amount field is greater than zero</div>
            </div>
            <div className="border-l-2 border-tool-validator pl-4">
              <div className="font-mono text-xs text-muted-foreground">VAL-003</div>
              <div className="font-medium">Date Format Validation</div>
              <div className="text-sm text-muted-foreground">Validates date fields follow ISO 8601 format</div>
            </div>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
};
