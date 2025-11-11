import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ExternalLink, ArrowRight, Activity } from "lucide-react";
import { useNavigate } from "react-router-dom";

export const RouterTool = () => {
  const navigate = useNavigate();

  const handleLaunch = () => {
    navigate("/embed/router");
  };

  return (
    <div className="space-y-6">
      {/* Launcher Card */}
      <Card className="border-tool-router/30 bg-tool-router/5">
        <CardHeader>
          <CardTitle className="text-tool-router">Router Workbench</CardTitle>
          <CardDescription>
            Full-featured intake router for tagging payloads and forwarding to correct destinations. 
            Supports file uploads, JSON payloads, and API requests with intelligent routing logic.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card border">
              <Activity className="h-5 w-5 text-tool-router" />
              <div>
                <div className="text-sm font-medium">Active Routes</div>
                <div className="text-xs text-muted-foreground">3 destinations</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card border">
              <Activity className="h-5 w-5 text-tool-router" />
              <div>
                <div className="text-sm font-medium">Today's Activity</div>
                <div className="text-xs text-muted-foreground">12 payloads routed</div>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-card border">
              <Activity className="h-5 w-5 text-tool-router" />
              <div>
                <div className="text-sm font-medium">Success Rate</div>
                <div className="text-xs text-muted-foreground">98.5%</div>
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button 
              className="flex-1 bg-tool-router text-tool-router-foreground hover:bg-tool-router/90 gap-2"
              onClick={handleLaunch}
            >
              Launch Router Workbench
              <ArrowRight className="h-4 w-4" />
            </Button>
            <Button 
              variant="outline"
              className="gap-2 border-tool-router/30 hover:bg-tool-router/10"
              onClick={() => window.open("https://messyflow-workbench.lovable.app", "_blank")}
            >
              <ExternalLink className="h-4 w-4" />
              Open in New Tab
            </Button>
          </div>

          <p className="text-xs text-muted-foreground">
            The Router Workbench runs as a standalone application with its own interface and backend integration.
          </p>
        </CardContent>
      </Card>
    </div>
  );
};
