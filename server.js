const express = require('express');
const { spawn } = require('child_process');
const app = express();
const port = 3000;

app.use(express.json());
app.use(express.static('public'));

let timeoutId = null;

app.post('/check-wallet', (req, res) => {
    const { mnemonic, network = 'mainnet' } = req.body;
    
    // Очищаем предыдущий таймаут
    if (timeoutId) {
        clearTimeout(timeoutId);
    }
    
    // Устанавливаем новый таймаут 20мс
    timeoutId = setTimeout(() => {
        const python = spawn('python3', ['wallet.py', mnemonic, network]);
        
        let resultData = '';
        let errorData = '';
        
        python.stdout.on('data', (data) => {
            resultData += data.toString();
        });
        
        python.stderr.on('data', (data) => {
            errorData += data.toString();
        });
        
        python.on('close', (code) => {
            if (code === 0) {
                try {
                    const parsed = JSON.parse(resultData);
                    res.json(parsed);
                } catch (e) {
                    res.json({error: 'Invalid JSON response', raw: resultData});
                }
            } else {
                res.json({error: errorData || 'Python script failed'});
            }
        });
    }, 20); // 20ms задержка после последнего ввода
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
