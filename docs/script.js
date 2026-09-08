const button = document.querySelector('#copy');
button?.addEventListener('click', async () => {
  await navigator.clipboard.writeText(document.querySelector('#command').textContent);
  button.textContent = 'Copied';
  setTimeout(() => (button.textContent = 'Copy'), 1400);
});
