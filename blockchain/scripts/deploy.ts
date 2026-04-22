import { ethers } from "hardhat";

async function main() {
    console.log("🚀 Deploying MediChainRecords...");

    // Get deployer account
    const [deployer] = await ethers.getSigners();
    console.log(`📝 Deploying with account: ${deployer.address}`);
    
    // Use deployer as gas wallet for local testing
    const gasWallet = deployer.address;
    console.log(`⛽ Gas wallet: ${gasWallet}`);

    const MediChainRecords = await ethers.getContractFactory("MediChainRecords");
    const contract = await MediChainRecords.deploy(gasWallet);
    await contract.waitForDeployment();

    const address = await contract.getAddress();
    console.log(`\n✅ MediChainRecords deployed to: ${address}`);
    console.log(`\n💾 Save this in your .env file:`);
    console.log(`CONTRACT_ADDRESS=${address}`);
    console.log(`GAS_WALLET_ADDRESS=${gasWallet}`);
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
