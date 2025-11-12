# Test de Health Endpoints HTTP
# Asegúrate de que el servidor esté corriendo en http://localhost:8000

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "🏥 TEST DE HEALTH ENDPOINTS - FastAPI" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""

$baseUrl = "http://localhost:8000/api/health"

# Lista de endpoints a probar
$endpoints = @(
    @{Name="Health General"; Path=""},
    @{Name="Database"; Path="/database"},
    @{Name="AI Model"; Path="/ai-model"},
    @{Name="Web Extractor"; Path="/web-extractor"},
    @{Name="NER Service"; Path="/ner-service"},
    @{Name="Wikipedia API"; Path="/wikipedia-api"},
    @{Name="NewsAPI"; Path="/news-api"},
    @{Name="Political Detector"; Path="/political-detector"},
    @{Name="Verification Layers"; Path="/verification-layers"}
)

$results = @()

foreach ($endpoint in $endpoints) {
    $url = "$baseUrl$($endpoint.Path)"
    Write-Host "`n🔍 Testing: $($endpoint.Name)" -ForegroundColor Yellow
    Write-Host "   URL: $url" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $url -Method Get -TimeoutSec 10
        
        $status = $response.status
        $symbol = if ($status -eq "healthy") { "✅" } 
                  elseif ($status -eq "degraded") { "⚠️ " } 
                  else { "❌" }
        
        Write-Host "   $symbol Status: $status" -ForegroundColor $(
            if ($status -eq "healthy") { "Green" }
            elseif ($status -eq "degraded") { "Yellow" }
            else { "Red" }
        )
        
        # Mostrar información adicional según el endpoint
        if ($endpoint.Path -eq "/ner-service") {
            Write-Host "   📊 spaCy Model: $($response.model_name)" -ForegroundColor Gray
            Write-Host "   📊 Database Entries: $($response.database_entries)" -ForegroundColor Gray
        }
        elseif ($endpoint.Path -eq "/wikipedia-api") {
            Write-Host "   📊 User-Agent: $($response.user_agent)" -ForegroundColor Gray
        }
        elseif ($endpoint.Path -eq "/news-api") {
            Write-Host "   📊 API Key Configured: $($response.api_key_configured)" -ForegroundColor Gray
        }
        elseif ($endpoint.Path -eq "/verification-layers") {
            Write-Host "   📊 Active: $($response.active_components)/$($response.total_components)" -ForegroundColor Gray
            Write-Host "   📊 Availability: $($response.availability_percentage)%" -ForegroundColor Gray
        }
        
        $results += @{
            Name = $endpoint.Name
            Status = $status
            Success = $true
        }
    }
    catch {
        Write-Host "   ❌ Error: $($_.Exception.Message)" -ForegroundColor Red
        $results += @{
            Name = $endpoint.Name
            Status = "error"
            Success = $false
        }
    }
}

# Resumen
Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host "📊 RESUMEN" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan

$healthyCount = ($results | Where-Object { $_.Status -eq "healthy" }).Count
$degradedCount = ($results | Where-Object { $_.Status -eq "degraded" }).Count
$unhealthyCount = ($results | Where-Object { $_.Status -eq "unhealthy" }).Count
$errorCount = ($results | Where-Object { $_.Success -eq $false }).Count
$total = $results.Count

Write-Host "`n✅ Healthy:   $healthyCount" -ForegroundColor Green
Write-Host "⚠️  Degraded:  $degradedCount" -ForegroundColor Yellow
Write-Host "❌ Unhealthy: $unhealthyCount" -ForegroundColor Red
Write-Host "🔴 Errors:    $errorCount" -ForegroundColor Magenta

$percentage = [math]::Round(($healthyCount / $total) * 100)
Write-Host "`nDisponibilidad: $percentage%" -ForegroundColor $(
    if ($percentage -ge 90) { "Green" }
    elseif ($percentage -ge 70) { "Yellow" }
    else { "Red" }
)

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 59 -ForegroundColor Cyan
Write-Host ""
