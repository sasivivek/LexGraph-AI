/**
 * Data Ingestion Script
 * Run with: npm run ingest
 */
const { verifyConnection, closeDriver } = require('../src/db/neo4jClient');
const { initSchema, clearDatabase } = require('../src/db/schema');
const { ingestAll } = require('../src/db/ingest');

async function main() {
  console.log('\n🏛️  LexGraph AI — Data Ingestion\n');
  console.log('================================\n');

  // Step 1: Verify connection
  const connected = await verifyConnection();
  if (!connected) {
    console.error('\n❌ Cannot connect to Neo4j. Please ensure it is running.');
    console.error('   URI:', process.env.NEO4J_URI || 'bolt://localhost:7687');
    process.exit(1);
  }

  // Step 2: Clear existing data
  console.log('\n📦 Step 1: Clearing existing data...');
  await clearDatabase();

  // Step 3: Create schema
  console.log('\n📐 Step 2: Creating schema...');
  await initSchema();

  // Step 4: Ingest all data
  console.log('\n📥 Step 3: Ingesting data...\n');
  await ingestAll();

  console.log('\n✅ Data ingestion complete!\n');
  console.log('You can now start the server with: npm start\n');

  await closeDriver();
  process.exit(0);
}

main().catch((error) => {
  console.error('Ingestion failed:', error);
  process.exit(1);
});
