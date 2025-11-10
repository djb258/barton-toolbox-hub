import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Upload, Save } from "lucide-react";
import { toast } from "sonner";

export const MapperTool = () => {
  const handleSaveMapping = () => {
    toast.success("Mapping saved", {
      description: "Field mapping recipe stored in Neon"
    });
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-tool-mapper/20 bg-tool-mapper/5 p-6">
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="csv-upload">Upload CSV/Data File</Label>
            <div className="flex gap-2">
              <Input id="csv-upload" type="file" />
              <Button variant="outline" size="icon">
                <Upload className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <div className="rounded-lg border bg-card p-4">
            <h4 className="text-sm font-semibold mb-3">Field Mapping</h4>
            <div className="space-y-3">
              <div className="grid grid-cols-3 gap-4 items-center">
                <Input placeholder="Source Field" defaultValue="customer_name" />
                <span className="text-center text-muted-foreground">→</span>
                <Input placeholder="Target Field" defaultValue="entity_name" />
              </div>
              <div className="grid grid-cols-3 gap-4 items-center">
                <Input placeholder="Source Field" defaultValue="invoice_amt" />
                <span className="text-center text-muted-foreground">→</span>
                <Input placeholder="Target Field" defaultValue="amount" />
              </div>
            </div>
          </div>

          <Button 
            className="bg-tool-mapper text-tool-mapper-foreground hover:bg-tool-mapper/90"
            onClick={handleSaveMapping}
          >
            <Save className="mr-2 h-4 w-4" />
            Save Mapping to Neon
          </Button>
        </div>
      </div>

      <div className="rounded-lg border bg-card">
        <div className="border-b bg-muted/50 px-4 py-3">
          <h3 className="text-sm font-semibold">Saved Mapping Recipes</h3>
        </div>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Recipe Name</TableHead>
              <TableHead>Source Schema</TableHead>
              <TableHead>Target Schema</TableHead>
              <TableHead>Fields Mapped</TableHead>
              <TableHead>Last Updated</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell className="font-medium">Invoice Import</TableCell>
              <TableCell className="font-mono text-xs">CSV_V1</TableCell>
              <TableCell className="font-mono text-xs">STAMPED</TableCell>
              <TableCell>12</TableCell>
              <TableCell className="font-mono text-xs">2025-11-08</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
