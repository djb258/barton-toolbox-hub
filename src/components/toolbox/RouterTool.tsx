import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Send } from "lucide-react";
import { toast } from "sonner";

export const RouterTool = () => {
  const handleSendPayload = () => {
    toast.success("Payload routed successfully", {
      description: "Data forwarded to validator"
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-tool-router/20 bg-tool-router/5 p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="input-type">Input Type</Label>
            <Select>
              <SelectTrigger id="input-type">
                <SelectValue placeholder="Select input type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="file">File Upload</SelectItem>
                <SelectItem value="json">JSON Payload</SelectItem>
                <SelectItem value="api">API Request</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="destination">Destination</Label>
            <Select>
              <SelectTrigger id="destination">
                <SelectValue placeholder="Select destination" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="validator">Validator</SelectItem>
                <SelectItem value="n8n">n8n Workflow</SelectItem>
                <SelectItem value="sheets">Google Sheets</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="batch-id">Batch ID</Label>
            <Input id="batch-id" placeholder="Auto-generated" disabled />
          </div>

          <div className="space-y-2">
            <Label htmlFor="source-entity">Source Entity</Label>
            <Input id="source-entity" placeholder="Enter source entity" />
          </div>
        </div>

        <Button 
          className="mt-4 bg-tool-router text-tool-router-foreground hover:bg-tool-router/90"
          onClick={handleSendPayload}
        >
          <Send className="mr-2 h-4 w-4" />
          Send Payload
        </Button>
      </div>

      <div className="rounded-lg border bg-card">
        <div className="border-b bg-muted/50 px-4 py-3">
          <h3 className="text-sm font-semibold">Recent Router Logs</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Batch ID</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Destination</TableHead>
              <TableHead>Status</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-mono text-xs">2025-11-10 14:23:01</TableCell>
              <TableCell className="font-mono text-xs">BTX-20251110-001</TableCell>
              <TableCell>API Upload</TableCell>
              <TableCell>Validator</TableCell>
              <TableCell>
                <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                  Success
                </span>
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
