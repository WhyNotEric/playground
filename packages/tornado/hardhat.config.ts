import { HardhatUserConfig } from 'hardhat/config'

import '@nomicfoundation/hardhat-toolbox'
import '@nomiclabs/hardhat-ethers'
import '@openzeppelin/hardhat-upgrades'
import 'hardhat-abi-exporter'

const deployerPriv =
  'cd632569e1c972446b0614c7ba2cdf971ea2fa26281c289328a9bca9c709129d'

const config: HardhatUserConfig = {
  solidity: {
    version: '0.8.9',
    settings: {
      optimizer: {
        enabled: true,
        runs: 10000,
      },
    },
  },
  networks: {
    hardhat: {},
    l1staging: {
      url: 'http://39.107.44.20:10545',
      accounts: [deployerPriv],
    },
    l2staging: {
      url: 'http://39.107.44.20:11545',
      accounts: [deployerPriv],
    },
  },
  abiExporter: {
    path: './abis',
    runOnCompile: true,
    clear: true,
    flat: true,
    only: [':Withdraw$', ':Verifier$'],
    spacing: 2,
    pretty: false,
  },
  paths: {
    sources: 'contracts',
  },
  typechain: {
    outDir: 'typechain-types',
    target: 'ethers-v5',
  },
  mocha: {
    timeout: 0,
  },
}

export default config
