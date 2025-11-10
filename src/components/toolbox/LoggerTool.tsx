import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Search } from "lucide-react";

export const LoggerTool = () => {
  return (
    <Tabs defaultValue="audit" className="w-full">
      <TabsList className="grid w-full grid-cols-3">
        <TabsTrigger value="audit">Audit Log</TabsTrigger>
        <TabsTrigger value="errors">Error Master</TabsTrigger>
        <TabsTrigger value="health">Health Monitor</TabsTrigger>
      </TabsList>

      <TabsContent value="audit" className="space-y-4">
        <div className="flex gap-2">
          <div className="flex-1">
            <Label htmlFor="date-range" className="sr-only">Date Range</Label>
            <Input id="date-range" type="date" />
          </div>
          <div className="flex-1">
            <Label htmlFor="tool-filter" className="sr-only">Tool Filter</Label>
            <Input id="tool-filter" placeholder="Filter by tool..." />
          </div>
          <Button variant="outline">
            <Search className="h-4 w-4" />
          </Button>
        </div>

        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>Tool ID</TableHead>
                <TableHead>Process ID</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs">2025-11-10 14:35:22</TableCell>
                <TableCell className="font-medium">router</TableCell>
                <TableCell className="font-mono text-xs">PROC-001</TableCell>
                <TableCell>Forward payload</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                    Success
                  </span>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-mono text-xs">2025-11-10 14:30:15</TableCell>
                <TableCell className="font-medium">validator</TableCell>
                <TableCell className="font-mono text-xs">PROC-002</TableCell>
                <TableCell>Run validation</TableCell>
                <TableCell>
                  <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700">
                    Success
                  </span>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </TabsContent>

      <TabsContent value="errors" className="space-y-4">
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Error ID</TableHead>
                <TableHead>Tool</TableHead>
                <TableHead>Error Type</TableHead>
                <TableHead>Message</TableHead>
                <TableHead>Timestamp</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-mono text-xs">ERR-20251110-003</TableCell>
                <TableCell className="font-medium">validator</TableCell>
                <TableCell>ValidationError</TableCell>
                <TableCell className="text-red-600">Invalid email format in record REC-00127</TableCell>
                <TableCell className="font-mono text-xs">2025-11-10 14:30:15</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </TabsContent>

      <TabsContent value="health" className="space-y-4">
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Last Validator Run</div>
            <div className="text-2xl font-bold mt-1">5 min ago</div>
            <div className="text-xs text-green-600 mt-1">✓ Healthy</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Success Rate (24h)</div>
            <div className="text-2xl font-bold mt-1">98.3%</div>
            <div className="text-xs text-green-600 mt-1">✓ Normal</div>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <div className="text-sm text-muted-foreground">Active Processes</div>
            <div className="text-2xl font-bold mt-1">12</div>
            <div className="text-xs text-muted-foreground mt-1">Current load</div>
          </div>
        </div>
      </TabsContent>
    </Tabs>
  );
};
