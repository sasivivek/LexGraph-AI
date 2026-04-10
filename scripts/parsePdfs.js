/**
 * PDF Parsing Script
 * Extracts text from all PDFs and saves to JSON for inspection
 * Run with: npm run parse-pdfs
 */
const fs = require('fs');
const path = require('path');
const { extractAllPdfs } = require('../src/parsers/pdfParser');
const { parseActText } = require('../src/parsers/actParser');
const { parseAmendmentText } = require('../src/parsers/amendmentParser');
const { parseRulesText } = require('../src/parsers/rulesParser');

async function main() {
  console.log('\n📄 LexGraph AI — PDF Parsing\n');
  console.log('============================\n');

  const { actText, amendmentText, rulesText } = await extractAllPdfs();

  const outputDir = path.join(__dirname, '..', 'src', 'data');

  // Save raw text for inspection
  if (actText) {
    fs.writeFileSync(path.join(outputDir, 'act_raw.txt'), actText, 'utf-8');
    console.log('💾 Saved: act_raw.txt');

    const parsed = parseActText(actText);
    if (parsed) {
      fs.writeFileSync(path.join(outputDir, 'act_parsed.json'), JSON.stringify(parsed, null, 2), 'utf-8');
      console.log('💾 Saved: act_parsed.json');
    }
  }

  if (amendmentText) {
    fs.writeFileSync(path.join(outputDir, 'amendment_raw.txt'), amendmentText, 'utf-8');
    console.log('💾 Saved: amendment_raw.txt');

    const parsed = parseAmendmentText(amendmentText);
    if (parsed) {
      fs.writeFileSync(path.join(outputDir, 'amendment_parsed.json'), JSON.stringify(parsed, null, 2), 'utf-8');
      console.log('💾 Saved: amendment_parsed.json');
    }
  }

  if (rulesText) {
    fs.writeFileSync(path.join(outputDir, 'rules_raw.txt'), rulesText, 'utf-8');
    console.log('💾 Saved: rules_raw.txt');

    const parsed = parseRulesText(rulesText);
    if (parsed) {
      fs.writeFileSync(path.join(outputDir, 'rules_parsed.json'), JSON.stringify(parsed, null, 2), 'utf-8');
      console.log('💾 Saved: rules_parsed.json');
    }
  }

  console.log('\n✅ PDF parsing complete!\n');
}

main().catch(console.error);
