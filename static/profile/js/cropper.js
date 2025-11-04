/**
 * Profile Picture Cropper JavaScript Component
 * Handles advanced image cropping with circular mask
 */

class ProfilePictureCropper {
    constructor(options = {}) {
        this.options = {
            imageId: options.imageId || 'crop-image',
            containerId: options.containerId || 'cropper-container',
            previewId: options.previewId || 'crop-preview',
            aspectRatio: options.aspectRatio || 1,
            minSize: options.minSize || 100,
            maxSize: options.maxSize || 2000,
            onCropChange: options.onCropChange || this.defaultCropChangeHandler,
            onCropComplete: options.onCropComplete || this.defaultCropCompleteHandler,
            ...options
        };

        this.image = document.getElementById(this.options.imageId);
        this.container = document.getElementById(this.options.containerId);
        this.preview = document.getElementById(this.options.previewId);
        this.cropper = null;
        this.cropData = null;

        this.init();
    }

    init() {
        if (!this.image || !this.container) {
            console.error('Required elements not found for cropper initialization');
            return;
        }

        this.setupCropper();
        this.setupControls();
    }

    setupCropper() {
        if (typeof Cropper === 'undefined') {
            console.error('Cropper.js is not loaded');
            return;
        }

        this.cropper = new Cropper(this.image, {
            aspectRatio: this.options.aspectRatio,
            viewMode: 2,
            dragMode: 'move',
            autoCrop: true,
            autoCropArea: 0.8,
            restore: false,
            guides: true,
            center: true,
            highlight: true,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: true,
            minCropBoxWidth: this.options.minSize,
            minCropBoxHeight: this.options.minSize,
            minContainerWidth: 300,
            minContainerHeight: 300,
            ready: () => {
                this.onCropperReady();
            },
            crop: (event) => {
                this.onCropChange(event);
            },
            cropend: (event) => {
                this.onCropComplete(event);
            }
        });
    }

    setupControls() {
        // Add control buttons if they don't exist
        if (!this.container.querySelector('.cropper-controls')) {
            const controls = document.createElement('div');
            controls.className = 'cropper-controls';
            controls.innerHTML = `
                <div class="control-group">
                    <button type="button" class="btn btn-sm btn-secondary" data-action="zoom-in">
                        <i class="icon">+</i> Zoom In
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary" data-action="zoom-out">
                        <i class="icon">-</i> Zoom Out
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary" data-action="reset">
                        <i class="icon">⟲</i> Reset
                    </button>
                </div>
                <div class="control-group">
                    <button type="button" class="btn btn-sm btn-secondary" data-action="rotate-left">
                        <i class="icon">↺</i> Rotate Left
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary" data-action="rotate-right">
                        <i class="icon">↻</i> Rotate Right
                    </button>
                </div>
                <div class="control-group">
                    <button type="button" class="btn btn-sm btn-secondary" data-action="flip-horizontal">
                        <i class="icon">↔</i> Flip H
                    </button>
                    <button type="button" class="btn btn-sm btn-secondary" data-action="flip-vertical">
                        <i class="icon">↕</i> Flip V
                    </button>
                </div>
            `;

            this.container.appendChild(controls);
            this.bindControlEvents();
        }
    }

    bindControlEvents() {
        const controls = this.container.querySelector('.cropper-controls');
        if (!controls) return;

        controls.addEventListener('click', (e) => {
            const button = e.target.closest('button');
            if (!button) return;

            const action = button.dataset.action;
            this.handleControlAction(action);
        });
    }

    handleControlAction(action) {
        if (!this.cropper) return;

        switch (action) {
            case 'zoom-in':
                this.cropper.zoom(0.1);
                break;
            case 'zoom-out':
                this.cropper.zoom(-0.1);
                break;
            case 'reset':
                this.cropper.reset();
                break;
            case 'rotate-left':
                this.cropper.rotate(-90);
                break;
            case 'rotate-right':
                this.cropper.rotate(90);
                break;
            case 'flip-horizontal':
                this.cropper.scaleX(-this.cropper.getData().scaleX || -1);
                break;
            case 'flip-vertical':
                this.cropper.scaleY(-this.cropper.getData().scaleY || -1);
                break;
        }
    }

    onCropperReady() {
        console.log('Cropper is ready');
        this.updatePreview();
    }

    onCropChange(event) {
        this.cropData = event.detail;
        this.options.onCropChange(this.cropData);
        this.updatePreview();
    }

    onCropComplete(event) {
        this.cropData = event.detail;
        this.options.onCropComplete(this.cropData);
    }

    updatePreview() {
        if (!this.preview || !this.cropper) return;

        const canvas = this.cropper.getCroppedCanvas({
            width: 200,
            height: 200,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high'
        });

        if (canvas) {
            // Create circular preview
            const circularCanvas = document.createElement('canvas');
            const size = 200;
            circularCanvas.width = size;
            circularCanvas.height = size;
            
            const ctx = circularCanvas.getContext('2d');
            
            // Draw circular mask
            ctx.beginPath();
            ctx.arc(size / 2, size / 2, size / 2, 0, 2 * Math.PI);
            ctx.closePath();
            ctx.clip();
            
            // Draw the image
            ctx.drawImage(canvas, 0, 0, size, size);
            
            // Update preview
            this.preview.innerHTML = '';
            const previewImg = document.createElement('img');
            previewImg.src = circularCanvas.toDataURL('image/jpeg', 0.9);
            previewImg.className = 'circular-preview';
            this.preview.appendChild(previewImg);
        }
    }

    getCropData() {
        if (!this.cropper) return null;
        
        const data = this.cropper.getData(true);
        return {
            x: Math.round(data.x),
            y: Math.round(data.y),
            width: Math.round(data.width),
            height: Math.round(data.height),
            scaleX: data.scaleX,
            scaleY: data.scaleY,
            rotate: data.rotate
        };
    }

    getCropCoords() {
        const data = this.getCropData();
        if (!data) return null;
        
        return `${data.x},${data.y},${data.width},${data.height}`;
    }

    getCroppedCanvas(options = {}) {
        if (!this.cropper) return null;
        
        const defaultOptions = {
            width: 300,
            height: 300,
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high',
            ...options
        };

        return this.cropper.getCroppedCanvas(defaultOptions);
    }

    getCroppedBlob(callback, mimeType = 'image/jpeg', quality = 0.9) {
        const canvas = this.getCroppedCanvas();
        if (!canvas) {
            callback(null);
            return;
        }

        canvas.toBlob(callback, mimeType, quality);
    }

    reset() {
        if (this.cropper) {
            this.cropper.reset();
        }
    }

    destroy() {
        if (this.cropper) {
            this.cropper.destroy();
            this.cropper = null;
        }
    }

    // Static method to create cropper from image URL
    static fromImageUrl(imageUrl, options = {}) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const container = document.createElement('div');
                container.style.position = 'relative';
                container.style.maxWidth = '100%';
                container.style.margin = '0 auto';
                
                img.id = options.imageId || 'crop-image';
                img.style.maxWidth = '100%';
                img.style.height = 'auto';
                
                container.appendChild(img);
                
                if (options.containerId) {
                    const existingContainer = document.getElementById(options.containerId);
                    if (existingContainer) {
                        existingContainer.innerHTML = '';
                        existingContainer.appendChild(container);
                    }
                }
                
                const cropper = new ProfilePictureCropper({
                    ...options,
                    imageId: img.id,
                    containerId: options.containerId
                });
                
                resolve(cropper);
            };
            
            img.onerror = () => {
                reject(new Error('Failed to load image'));
            };
            
            img.src = imageUrl;
        });
    }

    // Default handlers
    defaultCropChangeHandler(data) {
        console.log('Crop changed:', data);
    }

    defaultCropCompleteHandler(data) {
        console.log('Crop completed:', data);
    }
}

// Utility functions
window.ProfilePictureCropper = ProfilePictureCropper;

// Helper function to initialize cropper with common options
window.initProfileCropper = function(options = {}) {
    const defaultOptions = {
        aspectRatio: 1,
        minSize: 100,
        maxSize: 2000,
        onCropChange: function(data) {
            // Update crop info display
            const infoElement = document.getElementById('crop-info');
            if (infoElement) {
                infoElement.innerHTML = `
                    <small>
                        Position: (${Math.round(data.x)}, ${Math.round(data.y)})<br>
                        Size: ${Math.round(data.width)} × ${Math.round(data.height)}<br>
                        Rotation: ${data.rotate}°
                    </small>
                `;
            }
        }
    };

    return new ProfilePictureCropper({...defaultOptions, ...options});
};
