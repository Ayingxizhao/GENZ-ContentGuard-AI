#!/usr/bin/env node

// Development script for automatic extension reloading
// Run with: node dev-script.js

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');

class ExtensionDevScript {
    constructor() {
        this.watchedFiles = new Set();
        this.lastModified = {};
        this.isReloading = false;
        this.init();
    }

    init() {
        console.log('🛠️ Extension Development Script Started');
        console.log('📁 Watching for changes in extension files...');
        
        this.watchDirectory('extension');
        this.setupKeyboardShortcuts();
    }

    watchDirectory(dir) {
        const files = this.getFilesRecursively(dir);
        
        files.forEach(file => {
            if (this.shouldWatchFile(file)) {
                this.watchFile(file);
            }
        });

        // Watch for new files
        fs.watch(dir, { recursive: true }, (eventType, filename) => {
            if (filename) {
                const fullPath = path.join(dir, filename);
                if (this.shouldWatchFile(fullPath)) {
                    this.watchFile(fullPath);
                }
            }
        });
    }

    getFilesRecursively(dir) {
        const files = [];
        
        const items = fs.readdirSync(dir);
        items.forEach(item => {
            const fullPath = path.join(dir, item);
            const stat = fs.statSync(fullPath);
            
            if (stat.isDirectory()) {
                files.push(...this.getFilesRecursively(fullPath));
            } else {
                files.push(fullPath);
            }
        });
        
        return files;
    }

    shouldWatchFile(file) {
        const ext = path.extname(file);
        return ['.js', '.html', '.css', '.json'].includes(ext) && 
               !file.includes('node_modules') &&
               !file.includes('.git');
    }

    watchFile(file) {
        if (this.watchedFiles.has(file)) return;
        
        this.watchedFiles.add(file);
        this.lastModified[file] = fs.statSync(file).mtime.getTime();
        
        fs.watchFile(file, (curr, prev) => {
            if (curr.mtime.getTime() !== this.lastModified[file]) {
                this.lastModified[file] = curr.mtime.getTime();
                this.onFileChanged(file);
            }
        });
        
        console.log(`👁️ Watching: ${file}`);
    }

    onFileChanged(file) {
        if (this.isReloading) return;
        
        console.log(`📝 File changed: ${file}`);
        this.reloadExtension();
    }

    async reloadExtension() {
        if (this.isReloading) return;
        
        this.isReloading = true;
        console.log('🔄 Reloading extension...');
        
        try {
            // Get Chrome extension ID (you'll need to set this)
            const extensionId = this.getExtensionId();
            
            if (extensionId) {
                // Reload extension using Chrome CLI
                exec(`chrome --reload-extension="${extensionId}"`, (error, stdout, stderr) => {
                    if (error) {
                        console.log('⚠️ Could not reload via CLI, please reload manually');
                        console.log('💡 Press Ctrl+R in chrome://extensions/');
                    } else {
                        console.log('✅ Extension reloaded successfully!');
                    }
                });
            } else {
                console.log('⚠️ Extension ID not found, please reload manually');
                console.log('💡 Press Ctrl+R in chrome://extensions/');
            }
        } catch (error) {
            console.error('❌ Failed to reload extension:', error);
        }
        
        // Reset reloading flag after a delay
        setTimeout(() => {
            this.isReloading = false;
        }, 2000);
    }

    getExtensionId() {
        // Try to get extension ID from various sources
        try {
            // Check if there's a stored extension ID
            const configPath = path.join(__dirname, 'extension-id.txt');
            if (fs.existsSync(configPath)) {
                const id = fs.readFileSync(configPath, 'utf8').trim();
                if (id && id.length > 0) {
                    return id;
                }
            }
            
            // Check dev-config.json
            const configFile = path.join(__dirname, 'dev-config.json');
            if (fs.existsSync(configFile)) {
                const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
                if (config.extensionId) {
                    return config.extensionId;
                }
            }
            
            return null;
        } catch (error) {
            console.error('Error reading extension ID:', error);
            return null;
        }
    }

    setupKeyboardShortcuts() {
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        console.log('\n⌨️ Development Commands:');
        console.log('  r - Reload extension');
        console.log('  q - Quit development script');
        console.log('  h - Show help');
        console.log('  i - Set extension ID');
        console.log('');

        rl.on('line', (input) => {
            const command = input.trim().toLowerCase();
            
            switch (command) {
                case 'r':
                    this.reloadExtension();
                    break;
                case 'q':
                    console.log('👋 Goodbye!');
                    process.exit(0);
                    break;
                case 'h':
                    this.showHelp();
                    break;
                case 'i':
                    this.setExtensionId();
                    break;
                default:
                    console.log('❓ Unknown command. Type "h" for help.');
            }
        });
    }

    showHelp() {
        console.log(`
🛠️ Extension Development Help:

Commands:
  r - Reload extension
  q - Quit development script
  h - Show this help
  i - Set extension ID

Tips:
  - The script automatically watches for file changes
  - Press Ctrl+R in chrome://extensions/ to reload manually
  - Set your extension ID for automatic reloading
  - Use Ctrl+Shift+R in browser to reload content scripts
        `);
    }

    setExtensionId() {
        const readline = require('readline');
        const rl = readline.createInterface({
            input: process.stdin,
            output: process.stdout
        });

        rl.question('Enter your extension ID: ', (id) => {
            const trimmedId = id.trim();
            if (trimmedId.length === 0) {
                console.log('❌ Extension ID cannot be empty');
                rl.close();
                return;
            }
            
            // Save to both files for compatibility
            const configPath = path.join(__dirname, 'extension-id.txt');
            fs.writeFileSync(configPath, trimmedId);
            
            // Also save to dev-config.json
            const configFile = path.join(__dirname, 'dev-config.json');
            let config = {};
            if (fs.existsSync(configFile)) {
                config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
            }
            config.extensionId = trimmedId;
            fs.writeFileSync(configFile, JSON.stringify(config, null, 2));
            
            console.log('✅ Extension ID saved to both files!');
            console.log(`📝 ID: ${trimmedId}`);
            rl.close();
        });
    }
}

// Start the development script
new ExtensionDevScript();
