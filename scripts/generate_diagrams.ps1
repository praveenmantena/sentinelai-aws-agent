Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
$Diagrams = Join-Path $Root 'diagrams'

function New-Node {
    param(
        [string]$Text,
        [int]$X,
        [int]$Y,
        [int]$W,
        [int]$H,
        [string]$Fill = '#E8F1F8'
    )

    [PSCustomObject]@{
        Text = $Text
        X = $X
        Y = $Y
        W = $W
        H = $H
        Fill = $Fill
    }
}

function Draw-Diagram {
    param(
        [string]$Path,
        [string]$Title,
        [array]$Nodes,
        [array]$Edges,
        [string]$Footer
    )

    $bitmap = New-Object System.Drawing.Bitmap 1600, 900
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.Clear([System.Drawing.ColorTranslator]::FromHtml('#F7F4EE'))

    $titleFont = New-Object System.Drawing.Font('Segoe UI', 28, [System.Drawing.FontStyle]::Bold)
    $bodyFont = New-Object System.Drawing.Font('Segoe UI', 14, [System.Drawing.FontStyle]::Regular)
    $smallFont = New-Object System.Drawing.Font('Segoe UI', 12, [System.Drawing.FontStyle]::Regular)
    $titleBrush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#102A43'))
    $linePen = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#486581'), 3)
    $linePen.CustomEndCap = New-Object System.Drawing.Drawing2D.AdjustableArrowCap(6, 6)

    $graphics.DrawString($Title, $titleFont, $titleBrush, 60, 35)

    foreach ($node in $Nodes) {
        $nodeX = [single]$node.X
        $nodeY = [single]$node.Y
        $nodeW = [single]$node.W
        $nodeH = [single]$node.H
        $fillBrush = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml($node.Fill))
        $borderPen = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#243B53'), 2)
        $graphics.FillRectangle($fillBrush, $nodeX, $nodeY, $nodeW, $nodeH)
        $graphics.DrawRectangle($borderPen, $nodeX, $nodeY, $nodeW, $nodeH)
        $textRect = [System.Drawing.RectangleF]::new($nodeX + 14, $nodeY + 12, $nodeW - 28, $nodeH - 24)
        $format = New-Object System.Drawing.StringFormat
        $format.Alignment = [System.Drawing.StringAlignment]::Center
        $format.LineAlignment = [System.Drawing.StringAlignment]::Center
        $graphics.DrawString($node.Text, $bodyFont, $titleBrush, $textRect, $format)
        $fillBrush.Dispose()
        $borderPen.Dispose()
        $format.Dispose()
    }

    foreach ($edge in $Edges) {
        $edgeX1 = [single]$edge.X1
        $edgeY1 = [single]$edge.Y1
        $edgeX2 = [single]$edge.X2
        $edgeY2 = [single]$edge.Y2
        $graphics.DrawLine($linePen, $edgeX1, $edgeY1, $edgeX2, $edgeY2)
        if ($edge.Label) {
            $labelX = [single](($edgeX1 + $edgeX2) / 2)
            $labelY = [single](($edgeY1 + $edgeY2) / 2) - 24
            $graphics.DrawString($edge.Label, $smallFont, $titleBrush, $labelX, $labelY)
        }
    }

    $footerRect = New-Object System.Drawing.RectangleF(60, 820, 1480, 40)
    $graphics.DrawString($Footer, $smallFont, $titleBrush, $footerRect)

    $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)

    $linePen.Dispose()
    $titleFont.Dispose()
    $bodyFont.Dispose()
    $smallFont.Dispose()
    $titleBrush.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

$systemNodes = @(
    (New-Node 'CloudWatch Alarm' 80 220 220 100 '#D9E2EC'),
    (New-Node 'EventBridge' 370 220 220 100 '#BCCCDC'),
    (New-Node 'Lambda AI Agent Service' 660 220 280 100 '#9FB3C8'),
    (New-Node 'Strands Multi-Agent Workflow' 1030 220 360 100 '#7B93AA'),
    (New-Node 'Bedrock' 1060 430 180 90 '#F7D9C4'),
    (New-Node 'Knowledge Base' 1270 430 180 90 '#F3C78B'),
    (New-Node 'DynamoDB Memory' 850 430 180 90 '#F0B67F'),
    (New-Node 'CloudWatch Logs' 640 430 180 90 '#FAD4C0')
)
$systemEdges = @(
    @{ X1 = 300; Y1 = 270; X2 = 370; Y2 = 270; Label = '' },
    @{ X1 = 590; Y1 = 270; X2 = 660; Y2 = 270; Label = '' },
    @{ X1 = 940; Y1 = 270; X2 = 1030; Y2 = 270; Label = '' },
    @{ X1 = 820; Y1 = 320; X2 = 730; Y2 = 430; Label = 'read logs' },
    @{ X1 = 1120; Y1 = 320; X2 = 1130; Y2 = 430; Label = 'invoke models' },
    @{ X1 = 1210; Y1 = 320; X2 = 1320; Y2 = 430; Label = 'retrieve docs' },
    @{ X1 = 1030; Y1 = 320; X2 = 940; Y2 = 430; Label = 'store memory' }
)
Draw-Diagram -Path (Join-Path $Diagrams 'system_architecture.png') -Title 'SentinelAI AWS Agent System Architecture' -Nodes $systemNodes -Edges $systemEdges -Footer 'Event-driven incident flow from CloudWatch alarm to multi-agent diagnosis with Bedrock-powered reasoning.'

$agentNodes = @(
    (New-Node 'Orchestrator Agent' 610 90 320 90 '#9FB3C8'),
    (New-Node 'Incident Detection Agent' 120 260 260 90 '#D9E2EC'),
    (New-Node 'Memory Agent' 450 260 220 90 '#BCCCDC'),
    (New-Node 'Log Analysis Agent' 740 260 240 90 '#D9E2EC'),
    (New-Node 'Knowledge Retrieval Agent' 1040 260 300 90 '#BCCCDC'),
    (New-Node 'Reasoning Agent' 450 470 240 90 '#F7D9C4'),
    (New-Node 'Remediation Agent' 840 470 240 90 '#F3C78B')
)
$agentEdges = @(
    @{ X1 = 770; Y1 = 180; X2 = 250; Y2 = 260; Label = '' },
    @{ X1 = 770; Y1 = 180; X2 = 560; Y2 = 260; Label = '' },
    @{ X1 = 770; Y1 = 180; X2 = 860; Y2 = 260; Label = '' },
    @{ X1 = 770; Y1 = 180; X2 = 1190; Y2 = 260; Label = '' },
    @{ X1 = 860; Y1 = 350; X2 = 570; Y2 = 470; Label = 'evidence' },
    @{ X1 = 1190; Y1 = 350; X2 = 570; Y2 = 470; Label = 'runbooks' },
    @{ X1 = 570; Y1 = 560; X2 = 960; Y2 = 560; Label = 'root cause' }
)
Draw-Diagram -Path (Join-Path $Diagrams 'agent_architecture.png') -Title 'Multi-Agent Orchestration' -Nodes $agentNodes -Edges $agentEdges -Footer 'The orchestrator coordinates specialist agents and preserves explainable intermediate observations.'

$ragNodes = @(
    (New-Node 'Alarm or User Query' 90 240 250 90 '#D9E2EC'),
    (New-Node 'Retrieve CloudWatch Logs' 420 160 280 90 '#BCCCDC'),
    (New-Node 'Retrieve Knowledge Base Docs' 420 330 280 90 '#BCCCDC'),
    (New-Node 'Compose Grounded Prompt' 820 240 280 90 '#9FB3C8'),
    (New-Node 'Bedrock Reasoning Model' 1190 240 280 90 '#F7D9C4'),
    (New-Node 'Diagnosis and Remediation' 1190 450 280 90 '#F3C78B')
)
$ragEdges = @(
    @{ X1 = 340; Y1 = 285; X2 = 420; Y2 = 205; Label = '' },
    @{ X1 = 340; Y1 = 285; X2 = 420; Y2 = 375; Label = '' },
    @{ X1 = 700; Y1 = 205; X2 = 820; Y2 = 285; Label = 'logs' },
    @{ X1 = 700; Y1 = 375; X2 = 820; Y2 = 285; Label = 'docs' },
    @{ X1 = 1100; Y1 = 285; X2 = 1190; Y2 = 285; Label = '' },
    @{ X1 = 1330; Y1 = 330; X2 = 1330; Y2 = 450; Label = 'answer' }
)
Draw-Diagram -Path (Join-Path $Diagrams 'rag_flow.png') -Title 'Retrieval Augmented Generation Workflow' -Nodes $ragNodes -Edges $ragEdges -Footer 'Logs and runbooks are fused into a grounded prompt before the Bedrock model generates a response.'

$awsNodes = @(
    (New-Node 'API Gateway' 80 140 220 90 '#D9E2EC'),
    (New-Node 'Lambda Runtime' 360 140 240 90 '#9FB3C8'),
    (New-Node 'EventBridge' 80 320 220 90 '#D9E2EC'),
    (New-Node 'CloudWatch Logs and Metrics' 360 320 300 90 '#BCCCDC'),
    (New-Node 'S3 Runbooks' 760 110 220 90 '#F7D9C4'),
    (New-Node 'Bedrock Knowledge Base' 1040 110 280 90 '#F3C78B'),
    (New-Node 'OpenSearch Serverless' 1370 110 180 90 '#F0B67F'),
    (New-Node 'DynamoDB Incident Memory' 760 320 260 90 '#F7D9C4'),
    (New-Node 'Amazon Bedrock Runtime' 1080 320 260 90 '#F3C78B')
)
$awsEdges = @(
    @{ X1 = 300; Y1 = 185; X2 = 360; Y2 = 185; Label = '' },
    @{ X1 = 300; Y1 = 365; X2 = 360; Y2 = 365; Label = '' },
    @{ X1 = 600; Y1 = 185; X2 = 760; Y2 = 155; Label = 'docs' },
    @{ X1 = 980; Y1 = 155; X2 = 1040; Y2 = 155; Label = '' },
    @{ X1 = 1320; Y1 = 155; X2 = 1370; Y2 = 155; Label = '' },
    @{ X1 = 600; Y1 = 185; X2 = 760; Y2 = 365; Label = 'memory' },
    @{ X1 = 600; Y1 = 185; X2 = 1080; Y2 = 365; Label = 'inference' },
    @{ X1 = 600; Y1 = 365; X2 = 360; Y2 = 365; Label = 'telemetry' }
)
Draw-Diagram -Path (Join-Path $Diagrams 'aws_service_integration.png') -Title 'AWS Service Integration' -Nodes $awsNodes -Edges $awsEdges -Footer 'API, eventing, retrieval, inference, storage, and observability layers are separated for production operability.'

Write-Host 'Generated PNG diagrams in the diagrams directory.'
