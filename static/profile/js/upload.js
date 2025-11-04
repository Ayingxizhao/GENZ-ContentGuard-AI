/**
 * Profile Picture Upload JavaScript Component
 * Handles file upload, validation, and preview functionality
 */

console.log('Profile upload script loaded!');

class ProfilePictureUpload {
    constructor(options = {}) {
        console.log('ProfilePictureUpload constructor called!', options);
        
        this.options = {
            dropZoneId: options.dropZoneId || 'profile-drop-zone',
            fileInputId: options.fileInputId || 'profile-file-input',
            previewId: options.previewId || 'profile-preview',
            uploadUrl: options.uploadUrl || '/api/profile/upload',
            validateUrl: options.validateUrl || '/api/profile/validate',
            maxFileSize: options.maxFileSize || 5 * 1024 * 1024, // 5MB
            allowedTypes: options.allowedTypes || ['image/jpeg', 'image/png', 'image/webp'],
            onSuccess: options.onSuccess || this.defaultSuccessHandler,
            onError: options.onError || this.defaultErrorHandler,
            onProgress: options.onProgress || this.defaultProgressHandler,
            ...options
        };

        this.dropZone = document.getElementById(this.options.dropZoneId);
        this.fileInput = document.getElementById(this.options.fileInputId);
        this.preview = document.getElementById(this.options.previewId);
        this.currentFile = null;
        this.cropper = null;

        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // File input change
        if (this.fileInput) {
            this.fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }

        // Drop zone click
        if (this.dropZone) {
            this.dropZone.addEventListener('click', () => {
                this.fileInput?.click();
            });
        }
    }

    setupDragAndDrop() {
        if (!this.dropZone) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropZone.addEventListener(eventName, () => {
                this.dropZone.classList.remove('drag-over');
            });
        });

        this.dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }

    handleFileSelect(file) {
        console.log('handleFileSelect called with file:', file.name, 'size:', file.size, 'type:', file.type);
        
        // Validate file
        if (file.size > this.options.maxFileSize) {
            this.options.onError(`File size exceeds ${this.formatFileSize(this.options.maxFileSize)}`);
            return;
        }

        if (!this.options.allowedTypes.includes(file.type)) {
            this.options.onError('File type not supported. Please use JPEG, PNG, or WebP.');
            return;
        }

        this.currentFile = file;
        this.showPreview(file);
        
        // Auto-upload after short delay
        setTimeout(() => {
            console.log('Auto-uploading file...');
            this.uploadFile();
        }, 500);
    }

    validateFile(file) {
        // Check file type
        if (!this.options.allowedTypes.includes(file.type)) {
            return {
                valid: false,
                error: `File type ${file.type} is not allowed. Please use JPEG, PNG, or WebP.`
            };
        }

        // Check file size
        if (file.size > this.options.maxFileSize) {
            const maxSizeMB = Math.round(this.options.maxFileSize / (1024 * 1024));
            return {
                valid: false,
                error: `File size exceeds ${maxSizeMB}MB limit.`
            };
        }

        return { valid: true };
    }

    showPreview(file) {
        if (!this.preview) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.preview.innerHTML = `
                <div class="preview-container">
                    <img src="${e.target.result}" alt="Preview" class="preview-image" />
                    <div class="preview-info">
                        <p class="file-name">${file.name}</p>
                        <p class="file-size">${this.formatFileSize(file.size)}</p>
                    </div>
                    <button type="button" class="remove-preview" onclick="profileUpload.removePreview()">
                        <i class="icon">×</i>
                    </button>
                </div>
            `;
            this.preview.classList.add('has-preview');
        };
        reader.readAsDataURL(file);
    }

    removePreview() {
        if (this.preview) {
            this.preview.innerHTML = '';
            this.preview.classList.remove('has-preview');
        }
        if (this.fileInput) {
            this.fileInput.value = '';
        }
        this.currentFile = null;
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }
    }

    async validateImageOnServer(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(this.options.validateUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (result.success) {
                this.options.onSuccess('Image validated successfully', result.info);
                this.setupCropper();
            } else {
                this.options.onError(result.error);
            }
        } catch (error) {
            this.options.onError('Failed to validate image: ' + error.message);
        }
    }

    setupCropper() {
        const previewImage = this.preview?.querySelector('.preview-image');
        if (!previewImage) return;

        // Initialize cropper if Cropper.js is available
        if (typeof Cropper !== 'undefined') {
            this.cropper = new Cropper(previewImage, {
                aspectRatio: 1,
                viewMode: 1,
                guides: true,
                center: true,
                highlight: true,
                background: true,
                autoCrop: true,
                movable: true,
                rotatable: true,
                scalable: true,
                zoomable: true,
                cropBoxMovable: true,
                cropBoxResizable: true,
                minCropBoxWidth: 100,
                minCropBoxHeight: 100,
                ready: () => {
                    this.showCropControls();
                }
            });
        }
    }

    showCropControls() {
        if (!this.preview) return;

        const controls = document.createElement('div');
        controls.className = 'crop-controls';
        controls.innerHTML = `
            <div class="crop-buttons">
                <button type="button" class="btn btn-secondary" onclick="profileUpload.resetCrop()">Reset</button>
                <button type="button" class="btn btn-primary" onclick="profileUpload.applyCrop()">Apply Crop</button>
            </div>
        `;

        this.preview.appendChild(controls);
    }

    resetCrop() {
        if (this.cropper) {
            this.cropper.reset();
        }
    }

    applyCrop() {
        if (!this.cropper || !this.currentFile) return;

        const cropData = this.cropper.getData(true);
        const cropCoords = `${Math.round(cropData.x)},${Math.round(cropData.y)},${Math.round(cropData.width)},${Math.round(cropData.height)}`;

        this.uploadFile(cropCoords);
    }

    async uploadFile(cropCoords = null) {
        if (!this.currentFile) return;

        console.log('Starting upload for file:', this.currentFile.name);
        
        const formData = new FormData();
        formData.append('file', this.currentFile);
        
        if (cropCoords) {
            formData.append('crop_coords', cropCoords);
        }

        const csrfToken = this.getCSRFToken();
        console.log('CSRF token:', csrfToken);

        this.showProgress();

        try {
            console.log('Sending request to:', this.options.uploadUrl);
            
            const response = await fetch(this.options.uploadUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': csrfToken
                }
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);

            const result = await response.json();
            console.log('Response data:', result);

            if (result.success) {
                console.log('Upload successful, calling success handler...');
                this.options.onSuccess('Profile picture uploaded successfully!', result);
            } else {
                console.log('Upload failed, calling error handler...');
                this.options.onError(result.error);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.options.onError('Upload failed: ' + error.message);
        } finally {
            this.hideProgress();
        }
    }

    showProgress() {
        const progressContainer = document.createElement('div');
        progressContainer.className = 'upload-progress';
        progressContainer.innerHTML = `
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
            <p class="progress-text">Uploading...</p>
        `;

        if (this.preview) {
            this.preview.appendChild(progressContainer);
        }
    }

    hideProgress() {
        const progressContainer = this.preview?.querySelector('.upload-progress');
        if (progressContainer) {
            progressContainer.remove();
        }
    }

    updateProgress(percent) {
        const progressFill = this.preview?.querySelector('.progress-fill');
        const progressText = this.preview?.querySelector('.progress-text');
        
        if (progressFill) {
            progressFill.style.width = `${percent}%`;
        }
        if (progressText) {
            progressText.textContent = `Uploading... ${percent}%`;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]');
        return token ? token.getAttribute('content') : '';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Default handlers
    defaultSuccessHandler(message, data) {
        console.log('Success:', message, data);
        // Show success message
        this.showMessage(message, 'success');
    }

    defaultErrorHandler(error) {
        console.error('Error:', error);
        // Show error message
        this.showMessage(error, 'error');
    }

    defaultProgressHandler(percent) {
        this.updateProgress(percent);
    }

    showMessage(message, type) {
        // Create or update message container
        let messageContainer = document.querySelector('.profile-upload-message');
        if (!messageContainer) {
            messageContainer = document.createElement('div');
            messageContainer.className = 'profile-upload-message';
            document.body.appendChild(messageContainer);
        }

        messageContainer.textContent = message;
        messageContainer.className = `profile-upload-message ${type}`;
        messageContainer.style.display = 'block';

        // Auto-hide after 5 seconds
        setTimeout(() => {
            messageContainer.style.display = 'none';
        }, 5000);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ProfilePictureUpload;
}
