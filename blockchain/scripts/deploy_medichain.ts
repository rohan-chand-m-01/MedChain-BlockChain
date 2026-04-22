import { ethers } from "hardhat";
import * as fs from "fs";
import * as path from "path";

async function main() {
    const [deployer, gasWallet] = await ethers.getSigners();
    
    console.log("🚀 Deploying MediChain Contracts");
    console.log("=====================================");
    console.log("Deployer address:", deployer.address);
    console.log("Gas Wallet address:", gasWallet.address);
    console.log("");

    // Get balances
    const deployerBalance = await ethers.provider.getBalance(deployer.address);
    const gasWalletBalance = await ethers.provider.getBalance(gasWallet.address);
    console.log("Deployer balance:", ethers.formatEther(deployerBalance), "ETH");
    console.log("Gas Wallet balance:", ethers.formatEther(gasWalletBalance), "ETH");
    console.log("");

    // 1. Deploy MediChainRecords with gas wallet
    console.log("📝 Deploying MediChainRecords...");
    const MediChainRecords = await ethers.getContractFactory("MediChainRecords");
    const records = await MediChainRecords.deploy(gasWallet.address);
    await records.waitForDeployment();
    const recordsAddress = await records.getAddress();
    console.log("✅ MediChainRecords deployed to:", recordsAddress);
    console.log("");

    // 2. Deploy ConsentRegistry with gas wallet
    console.log("📝 Deploying ConsentRegistry...");
    const ConsentRegistry = await ethers.getContractFactory("ConsentRegistry");
    const consent = await ConsentRegistry.deploy(gasWallet.address);
    await consent.waitForDeployment();
    const consentAddress = await consent.getAddress();
    console.log("✅ ConsentRegistry deployed to:", consentAddress);
    console.log("");

    // 3. Deploy MediToken (ERC20)
    console.log("📝 Deploying MediToken...");
    const MediToken = await ethers.getContractFactory("MediToken");
    const token = await MediToken.deploy();
    await token.waitForDeployment();
    const tokenAddress = await token.getAddress();
    console.log("✅ MediToken deployed to:", tokenAddress);
    console.log("");

    // 4. Deploy MediChainPayments
    console.log("📝 Deploying MediChainPayments...");
    const MediChainPayments = await ethers.getContractFactory("MediChainPayments");
    const payments = await MediChainPayments.deploy(tokenAddress, gasWallet.address);
    await payments.waitForDeployment();
    const paymentsAddress = await payments.getAddress();
    console.log("✅ MediChainPayments deployed to:", paymentsAddress);
    console.log("");

    // 5. Transfer some tokens to gas wallet for testing
    console.log("💰 Transferring 10,000 MEDI tokens to gas wallet...");
    const transferAmount = ethers.parseUnits("10000", 18);
    const transferTx = await token.transfer(gasWallet.address, transferAmount);
    await transferTx.wait();
    console.log("✅ Tokens transferred");
    console.log("");

    // 6. Save addresses to .env files
    console.log("💾 Saving contract addresses...");
    
    // Backend .env
    const backendEnvPath = path.join(__dirname, "../../backend/.env");
    let backendEnv = "";
    
    if (fs.existsSync(backendEnvPath)) {
        backendEnv = fs.readFileSync(backendEnvPath, "utf-8");
    }
    
    // Update or add contract addresses
    const updateEnvVar = (content: string, key: string, value: string): string => {
        const regex = new RegExp(`^${key}=.*$`, "m");
        if (regex.test(content)) {
            return content.replace(regex, `${key}=${value}`);
        } else {
            return content + `\n${key}=${value}`;
        }
    };
    
    backendEnv = updateEnvVar(backendEnv, "CONTRACT_ADDRESS", recordsAddress);
    backendEnv = updateEnvVar(backendEnv, "CONSENT_CONTRACT_ADDRESS", consentAddress);
    backendEnv = updateEnvVar(backendEnv, "PAYMENTS_CONTRACT_ADDRESS", paymentsAddress);
    backendEnv = updateEnvVar(backendEnv, "MEDI_TOKEN_ADDRESS", tokenAddress);
    backendEnv = updateEnvVar(backendEnv, "GAS_WALLET_ADDRESS", gasWallet.address);
    backendEnv = updateEnvVar(backendEnv, "ETHEREUM_RPC_URL", "http://127.0.0.1:8545");
    
    fs.writeFileSync(backendEnvPath, backendEnv);
    console.log("✅ Backend .env updated");
    
    // Frontend .env
    const frontendEnvPath = path.join(__dirname, "../../frontend/.env.local");
    let frontendEnv = "";
    
    if (fs.existsSync(frontendEnvPath)) {
        frontendEnv = fs.readFileSync(frontendEnvPath, "utf-8");
    }
    
    frontendEnv = updateEnvVar(frontendEnv, "NEXT_PUBLIC_CONTRACT_ADDRESS", recordsAddress);
    frontendEnv = updateEnvVar(frontendEnv, "NEXT_PUBLIC_CONSENT_CONTRACT_ADDRESS", consentAddress);
    frontendEnv = updateEnvVar(frontendEnv, "NEXT_PUBLIC_PAYMENTS_CONTRACT_ADDRESS", paymentsAddress);
    frontendEnv = updateEnvVar(frontendEnv, "NEXT_PUBLIC_MEDI_TOKEN_ADDRESS", tokenAddress);
    frontendEnv = updateEnvVar(frontendEnv, "NEXT_PUBLIC_ETHEREUM_RPC_URL", "http://127.0.0.1:8545");
    
    fs.writeFileSync(frontendEnvPath, frontendEnv);
    console.log("✅ Frontend .env.local updated");
    console.log("");

    // 7. Save deployment info to JSON
    const deploymentInfo = {
        network: "localhost",
        chainId: (await ethers.provider.getNetwork()).chainId.toString(),
        deployer: deployer.address,
        gasWallet: gasWallet.address,
        contracts: {
            MediChainRecords: recordsAddress,
            ConsentRegistry: consentAddress,
            MediToken: tokenAddress,
            MediChainPayments: paymentsAddress
        },
        timestamp: new Date().toISOString()
    };
    
    const deploymentPath = path.join(__dirname, "../deployments/localhost.json");
    fs.mkdirSync(path.dirname(deploymentPath), { recursive: true });
    fs.writeFileSync(deploymentPath, JSON.stringify(deploymentInfo, null, 2));
    console.log("✅ Deployment info saved to:", deploymentPath);
    console.log("");

    // Summary
    console.log("=====================================");
    console.log("🎉 Deployment Complete!");
    console.log("=====================================");
    console.log("MediChainRecords:", recordsAddress);
    console.log("ConsentRegistry:", consentAddress);
    console.log("MediToken:", tokenAddress);
    console.log("MediChainPayments:", paymentsAddress);
    console.log("");
    console.log("Gas Wallet:", gasWallet.address);
    console.log("Deployer:", deployer.address);
    console.log("");
    console.log("⚠️  IMPORTANT: Save the gas wallet private key!");
    console.log("Gas Wallet Private Key: [Check Hardhat accounts]");
    console.log("");
    console.log("Next steps:");
    console.log("1. Add GAS_WALLET_PRIVATE_KEY to backend/.env");
    console.log("2. Run database migrations");
    console.log("3. Test WhatsApp flow with blockchain persistence");
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
