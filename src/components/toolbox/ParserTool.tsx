import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Upload, SendHorizontal } from "lucide-react";
import { toast } from "sonner";

export const ParserTool = () => {
  const handleSendToValidator = () => {
    toast.success("Data sent to validator", {
      description: "Extracted JSON forwarded for validation"
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-tool-parser/20 bg-tool-parser/5 p-6">
        <div className="grid gap-4">
          <div className="space-y-2">
            <Label htmlFor="doc-upload">Upload Document (PDF/Doc)</Label>
            <div className="flex gap-2">
              <Input id="doc-upload" type="file" accept=".pdf,.doc,.docx" />
              <Button variant="outline" size="icon">
                <Upload className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="entity-type">Entity Type</Label>
            <Select>
              <SelectTrigger id="entity-type">
                <SelectValue placeholder="Select entity type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="invoice">Invoice</SelectItem>
                <SelectItem value="contract">Contract</SelectItem>
                <SelectItem value="receipt">Receipt</SelectItem>
                <SelectItem value="form">Form</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <div className="border-b bg-muted/50 px-4 py-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Extracted JSON Preview</h3>
          <Button 
            size="sm"
            className="bg-tool-parser text-tool-parser-foreground hover:bg-tool-parser/90"
            onClick={handleSendToValidator}
          >
            <SendHorizontal className="mr-2 h-4 w-4" />
            Send to Validator
          </Button>
        </div>
        <div className="p-4">
          <pre className="text-xs font-mono bg-muted p-4 rounded overflow-auto max-h-64">
{`{
  "document_type": "invoice",
  "entity_name": "Acme Corporation",
  "amount": 1250.00,
  "date": "2025-11-10",
  "invoice_number": "INV-2025-1234",
  "line_items": [
    {
      "description": "Professional Services",
      "quantity": 10,
      "unit_price": 125.00
    }
  ]
}`}
          </pre>
        </div>
      </div>
    </div>
  );
};
