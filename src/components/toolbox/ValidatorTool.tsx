import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { PlayCircle } from "lucide-react";
import { toast } from "sonner";

export const ValidatorTool = () => {
  const handleRunValidator = () => {
    toast.success("Validator executed", {
      description: "Processing 127 records"
    });
  };

  return (
    <Tabs defaultValue="rules" className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="rules">Rules</TabsTrigger>
        <TabsTrigger value="run">Run</TabsTrigger>
        <TabsTrigger value="results">Results</TabsTrigger>
        <TabsTrigger value="failed">Failed</TabsTrigger>
      </TabsList>

      <TabsContent value="rules" className="space-y-4">
        <div className="rounded-lg border bg-card">
          <div className="border-b bg-muted/50 px-4 py-3">
            <h3 className="text-sm font-semibold">Validation Rules</h3>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Rule ID</TableHead>
                <TableHead>Field</TableHead>
                <TableHead>Condition</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Active</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs">VAL-001</TableCell>
                <TableCell>email</TableCell>
                <TableCell className="font-mono text-xs">IS_EMAIL</TableCell>
                <TableCell>Reject</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                    Active
                  </span>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-mono text-xs">VAL-002</TableCell>
                <TableCell>amount</TableCell>
                <TableCell className="font-mono text-xs">{'> 0'}</TableCell>
                <TableCell>Flag</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                    Active
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </TabsContent>

      <TabsContent value="run" className="space-y-4">
        <div className="rounded-lg border border-tool-validator/20 bg-tool-validator/5 p-6">
          <p className="text-sm text-muted-foreground mb-4">
            Execute validation rules against current dataset. Results will be logged to audit system.
          </p>
          <Button 
            className="bg-tool-validator text-tool-validator-foreground hover:bg-tool-validator/90"
            onClick={handleRunValidator}
          >
            <PlayCircle className="mr-2 h-4 w-4" />
            Re-run Validation
          </Button>
        </div>
      </TabsContent>

      <TabsContent value="results" className="space-y-4">
        <div className="rounded-lg border bg-card">
          <div className="border-b bg-muted/50 px-4 py-3">
            <h3 className="text-sm font-semibold">Recent Validation Results</h3>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Run ID</TableHead>
                <TableHead>Timestamp</TableHead>
                <TableHead>Records</TableHead>
                <TableHead>Passed</TableHead>
                <TableHead>Failed</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs">RUN-20251110-003</TableCell>
                <TableCell className="font-mono text-xs">2025-11-10 14:30:15</TableCell>
                <TableCell>127</TableCell>
                <TableCell className="text-green-600 font-medium">124</TableCell>
                <TableCell className="text-red-600 font-medium">3</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </TabsContent>

      <TabsContent value="failed" className="space-y-4">
        <div className="rounded-lg border bg-card">
          <div className="border-b bg-muted/50 px-4 py-3">
            <h3 className="text-sm font-semibold">Failed Records</h3>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Record ID</TableHead>
                <TableHead>Field</TableHead>
                <TableHead>Rule Violated</TableHead>
                <TableHead>Error Message</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs">REC-00127</TableCell>
                <TableCell>email</TableCell>
                <TableCell className="font-mono text-xs">VAL-001</TableCell>
                <TableCell className="text-red-600 text-sm">Invalid email format</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </TabsContent>
    </Tabs>
  );
};
