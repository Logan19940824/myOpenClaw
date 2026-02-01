#!/usr/bin/env node
/**
 * Calculator MCP Skill
 * 
 * 通过 MCP 协议提供计算器功能
 * 
 * 输入格式 (stdin):
 * {
 *   "action": "add|sub|mul|div",
 *   "a": <number>,
 *   "b": <number>
 * }
 * 
 * 输出格式 (stdout):
 * {
 *   "result": <number>,
 *   "error": null | <string>
 * }
 */

const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

const operations = {
    add: (a, b) => a + b,
    sub: (a, b) => a - b,
    mul: (a, b) => a * b,
    div: (a, b) => b !== 0 ? a / b : null
};

function calculate(input) {
    return new Promise((resolve) => {
        try {
            const { action, a, b } = JSON.parse(input);
            
            if (!action || typeof a !== 'number' || typeof b !== 'number') {
                resolve(JSON.stringify({
                    result: null,
                    error: '无效的输入参数'
                }));
                return;
            }
            
            const operation = operations[action];
            
            if (!operation) {
                resolve(JSON.stringify({
                    result: null,
                    error: `未知的操作: ${action}`
                }));
                return;
            }
            
            const result = operation(a, b);
            
            if (result === null) {
                resolve(JSON.stringify({
                    result: null,
                    error: '除数不能为零'
                }));
                return;
            }
            
            resolve(JSON.stringify({
                result: result,
                error: null
            }));
            
        } catch (err) {
            resolve(JSON.stringify({
                result: null,
                error: `解析错误: ${err.message}`
            }));
        }
    });
}

rl.on('line', async (line) => {
    if (line.trim()) {
        const output = await calculate(line);
        console.log(output);
    }
});
