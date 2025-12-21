document.addEventListener('DOMContentLoaded', function() {
	const filterButtons = document.querySelectorAll('.filter-btn');
	filterButtons.forEach(btn => {
		btn.addEventListener('click', function() {
			filterButtons.forEach(b => b.classList.remove('active'));
			this.classList.add('active');
            
			const status = this.dataset.status;
			const items = document.querySelectorAll('.dialog-item');
            
			items.forEach(item => {
				if (status === 'all' || item.dataset.status === status) {
					item.style.display = 'block';
				} else {
					item.style.display = 'none';
				}
			});
		});
	});
    
	const statusSelect = document.getElementById('status-select');
	if (statusSelect) {
		statusSelect.addEventListener('change', async function() {
			const dialogId = this.dataset.dialogId;
			const status = this.value;
            
			const response = await fetch(`/dialog/${dialogId}/status`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ status })
			});
            
			if (response.ok) {
				alert('Статус оновлено');
			}
		});
	}
    
	const sendReplyBtn = document.getElementById('send-reply');
	if (sendReplyBtn) {
		sendReplyBtn.addEventListener('click', async function() {
			const dialogId = this.dataset.dialogId;
			const text = document.getElementById('reply-text').value;
            
			if (!text.trim()) {
				alert('Введіть текст повідомлення');
				return;
			}
            
			const response = await fetch(`/dialog/${dialogId}/reply`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ text })
			});
            
			if (response.ok) {
				location.reload();
			}
		});
	}
});
