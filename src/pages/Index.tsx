import { ToolHeader } from "@/components/toolbox/ToolHeader";
import { RouterTool } from "@/components/toolbox/RouterTool";
import { ValidatorTool } from "@/components/toolbox/ValidatorTool";
import { MapperTool } from "@/components/toolbox/MapperTool";
import { ParserTool } from "@/components/toolbox/ParserTool";
import { DocFillerTool } from "@/components/toolbox/DocFillerTool";
import { LoggerTool } from "@/components/toolbox/LoggerTool";
import { DocumentationTool } from "@/components/toolbox/DocumentationTool";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { 
  Route, 
  CheckCircle, 
  Map, 
  FileText, 
  FileEdit, 
  Database, 
  BookOpen,
  Edit2
} from "lucide-react";
import { Button } from "@/components/ui/button";

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <ToolHeader />
      
      <main className="container py-8 px-6">
        <div className="mb-8">
          <h2 className="text-2xl font-bold tracking-tight mb-2">Process Management Tools</h2>
          <p className="text-muted-foreground">
            Unified interface for routing, validation, mapping, and monitoring
          </p>
        </div>

        <Accordion type="single" collapsible className="space-y-4">
          <AccordionItem 
            value="router" 
            data-tool-id="router-tool"
            className="border border-tool-router/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-router/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-router text-tool-router-foreground">
                    <Route className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Router (Messy Logic)</div>
                    <div className="text-sm text-muted-foreground">
                      Intake router — tags payloads and forwards to correct destination
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-router hover:text-tool-router/80 hover:bg-tool-router/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Router Tool - ID: router-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <RouterTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="validator"
            data-tool-id="validator-tool"
            className="border border-tool-validator/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-validator/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-validator text-tool-validator-foreground">
                    <CheckCircle className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Validator (Neon Agent)</div>
                    <div className="text-sm text-muted-foreground">
                      Runs enrichment + validation rules stored in Neon
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-validator hover:text-tool-validator/80 hover:bg-tool-validator/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Validator Tool - ID: validator-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <ValidatorTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="mapper"
            data-tool-id="mapper-tool"
            className="border border-tool-mapper/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-mapper/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-mapper text-tool-mapper-foreground">
                    <Map className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Mapper</div>
                    <div className="text-sm text-muted-foreground">
                      Field mapping tool for CSV/API → STAMPED schema
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-mapper hover:text-tool-mapper/80 hover:bg-tool-mapper/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Mapper Tool - ID: mapper-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <MapperTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="parser"
            data-tool-id="parser-tool"
            className="border border-tool-parser/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-parser/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-parser text-tool-parser-foreground">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Parser</div>
                    <div className="text-sm text-muted-foreground">
                      PDF / Doc parser for extracting structured data
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-parser hover:text-tool-parser/80 hover:bg-tool-parser/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Parser Tool - ID: parser-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <ParserTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="docfiller"
            data-tool-id="docfiller-tool"
            className="border border-tool-docfiller/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-docfiller/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-docfiller text-tool-docfiller-foreground">
                    <FileEdit className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Doc Filler</div>
                    <div className="text-sm text-muted-foreground">
                      Fills templates with mapped data
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-docfiller hover:text-tool-docfiller/80 hover:bg-tool-docfiller/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Doc Filler Tool - ID: docfiller-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <DocFillerTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="logger"
            data-tool-id="logger-tool"
            className="border border-tool-logger/30 rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-tool-logger/5">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-tool-logger text-tool-logger-foreground">
                    <Database className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Logger / Monitor</div>
                    <div className="text-sm text-muted-foreground">
                      Central dashboard for audit + error tracking
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-tool-logger hover:text-tool-logger/80 hover:bg-tool-logger/10"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Logger Tool - ID: logger-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <LoggerTool />
            </AccordionContent>
          </AccordionItem>

          <AccordionItem 
            value="docs"
            data-tool-id="documentation-tool"
            className="border border-border rounded-lg bg-card overflow-hidden"
          >
            <AccordionTrigger className="px-6 py-4 hover:no-underline hover:bg-muted/30">
              <div className="flex items-center justify-between w-full">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-muted text-foreground">
                    <BookOpen className="h-5 w-5" />
                  </div>
                  <div className="text-left">
                    <div className="font-semibold">Documentation</div>
                    <div className="text-sm text-muted-foreground">
                      Self-documenting dashboard explaining how all tools tie together
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  onClick={(e) => {
                    e.stopPropagation();
                    alert('Edit Documentation Tool - ID: documentation-tool');
                  }}
                >
                  <Edit2 className="h-4 w-4" />
                </Button>
              </div>
            </AccordionTrigger>
            <AccordionContent className="px-6 pb-6">
              <DocumentationTool />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </main>
    </div>
  );
};

export default Index;
