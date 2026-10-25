param([string]$ReviewLabel='v22')
$ErrorActionPreference='Stop'
$reviewWord=$null
$reviewDoc=$null
$reviewRows=@()
try {
 $reviewWord=New-Object -ComObject Word.Application
 $reviewWord.Visible=$false
 $reviewWord.DisplayAlerts=0
 $reviewWord.AutomationSecurity=3
 $reviewWord.Options.SaveNormalPrompt=$false
 foreach($reviewName in @('Ear_Defender_Project','Glasses_Friendly_Headphone_Cushions')) {
  $reviewPath=Join-Path $PSScriptRoot ($reviewName+'.docx')
  $reviewHash=(Get-FileHash -LiteralPath $reviewPath -Algorithm SHA256).Hash.ToLowerInvariant()
  $reviewPdf=Join-Path $PSScriptRoot ('qa\native_'+$ReviewLabel+'_'+$reviewName+'.pdf')
  $reviewDoc=$reviewWord.Documents.Open($reviewPath,$false,$true,$false)
  $reviewDoc.Repaginate()
  $reviewPages=$reviewDoc.ComputeStatistics(2)
  $reviewDoc.ExportAsFixedFormat($reviewPdf,17)
  $reviewDoc.Close(0)
  $reviewDoc=$null
  if((Get-FileHash -LiteralPath $reviewPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $reviewHash) { throw 'Read-only source hash changed' }
  $reviewRows+=@{document=$reviewName;source_sha256=$reviewHash;native_pages=$reviewPages;pdf=$reviewPdf;pdf_sha256=(Get-FileHash -LiteralPath $reviewPdf -Algorithm SHA256).Hash.ToLowerInvariant();word_version=$reviewWord.Version;source_unchanged=$true;native_export='pass'}
 }
 $reviewResult=@{date='2026-10-25';documents=$reviewRows;scope='Native Word read-only export and pagination. Visual PDF review recorded separately.'}
 $reviewResult | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $PSScriptRoot 'qa\native_word_status.json') -Encoding utf8
 $reviewResult | ConvertTo-Json -Depth 8 | Write-Output
} finally {
 if($null -ne $reviewDoc) { $reviewDoc.Close(0) }
 if($null -ne $reviewWord) { $reviewWord.Quit(0);[System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($reviewWord) | Out-Null }
}
