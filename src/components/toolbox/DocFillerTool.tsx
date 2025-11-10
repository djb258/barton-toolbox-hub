import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { FileDown, Eye } from "lucide-react";
import { toast } from "sonner";

export const DocFillerTool = () => {
  const handleGenerate = () => {
    toast.success("Document generated", {
      description: "Template filled with mapped data"
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-tool-docfiller/20 bg-tool-docfiller/5 p-6">
        <div className="grid gap-4">
          <div className="space-y-2">
            <Label htmlFor="template-select">Select Template</Label>
            <Select>
              <SelectTrigger id="template-select">
                <SelectValue placeholder="Choose a template" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="invoice">Invoice Template</SelectItem>
                <SelectItem value="contract">Contract Template</SelectItem>
                <SelectItem value="report">Report Template</SelectItem>
                <SelectItem value="letter">Business Letter</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="data-source">Load Mapped Data</Label>
            <Select>
              <SelectTrigger id="data-source">
                <SelectValue placeholder="Select data source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="mapper">From Mapper</SelectItem>
                <SelectItem value="validator">From Validator</SelectItem>
                <SelectItem value="manual">Manual Entry</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex gap-2">
            <Button variant="outline" className="flex-1">
              <Eye className="mr-2 h-4 w-4" />
              Preview Document
            </Button>
            <Button 
              className="flex-1 bg-tool-docfiller text-tool-docfiller-foreground hover:bg-tool-docfiller/90"
              onClick={handleGenerate}
            >
              <FileDown className="mr-2 h-4 w-4" />
              Generate & Export
            </Button>
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <div className="border-b bg-muted/50 px-4 py-3">
          <h3 className="text-sm font-semibold">Document Preview</h3>
        </div>
        <div className="p-6 bg-white">
          <div className="prose prose-sm max-w-none">
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center text-muted-foreground">
              <p>Preview will appear here after selecting template and data source</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
