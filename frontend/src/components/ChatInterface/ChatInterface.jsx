import React, { useState, useEffect, useRef } from 'react';
import { Box, TextField, Button, Typography, List, ListItem, ListItemText, Avatar, IconButton, Paper, Divider, Chip, Snackbar, Alert } from '@mui/material';
import { Send as SendIcon, Clear as ClearIcon, Help as HelpIcon, Summarize as SummarizeIcon } from '@mui/icons-material';
import { chatApi, knowledgeApi } from '../../services/api';
import ReactMarkdown from 'react-markdown';

const ChatInterface = ({ selectedProject }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSummaryLoading, setIsSummaryLoading] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');
  const messagesEndRef = useRef(null);

  // 智能体列表
  const agents = selectedProject?.agents || ['理论导师', '实践教练', '数据分析师', '提问者', '历史学家'];

  // 滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 获取聊天历史
  const fetchChatHistory = async () => {
    if (!selectedProject) return;

    try {
      const response = await chatApi.getChatHistory(selectedProject.id);
      setMessages(response.data.messages);
      // 延迟滚动到底部，确保消息已渲染
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('获取聊天历史失败:', error);
    }
  };

  useEffect(() => {
    fetchChatHistory();
  }, [selectedProject]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedProject) return;

    try {
      setIsLoading(true);

      // 创建消息数据
      const messageData = {
        content: inputMessage.trim(),
        sender_type: 'user',
        sender_name: '用户',
        project_id: selectedProject.id,
      };

      // 发送消息到后端
      const response = await chatApi.sendMessage(messageData);

      // 更新消息列表
      setMessages([...response.data]);
      // 清空输入框
      setInputMessage('');

      // 延迟滚动到底部
      setTimeout(scrollToBottom, 100);
    } catch (error) {
      console.error('发送消息失败:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // 清空聊天历史
  const handleClearHistory = async () => {
    if (!selectedProject) return;

    try {
      await chatApi.clearChatHistory(selectedProject.id);
      setMessages([]);
    } catch (error) {
      console.error('清空聊天历史失败:', error);
    }
  };

  // 生成每日学习总结
  const handleGenerateSummary = async () => {
    if (!selectedProject) return;

    try {
      setIsSummaryLoading(true);

      // 调用后端API生成每日学习总结
      const response = await knowledgeApi.generateDailySummary(selectedProject.id);

      // 显示成功通知
      setSnackbarMessage('每日学习总结已生成并保存到知识库');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('生成每日学习总结失败:', error);
      // 显示错误通知
      setSnackbarMessage('生成每日学习总结失败，请稍后重试');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setIsSummaryLoading(false);
    }
  };

  // 处理Snackbar关闭
  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setSnackbarOpen(false);
  };

  // 插入@智能体
  const insertAgentMention = (agentName) => {
    setInputMessage(prev => `${prev}@${agentName} `);
  };

  // 处理键盘事件
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!selectedProject) {
    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="h6" color="text.secondary" align="center">
          请选择一个学习项目开始对话
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 项目标题和操作 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          {selectedProject.name}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            variant="outlined"
            startIcon={<SummarizeIcon />}
            onClick={handleGenerateSummary}
            disabled={isSummaryLoading || messages.length === 0}
            size="small"
          >
            {isSummaryLoading ? '生成中...' : '每日总结'}
          </Button>
          <IconButton
            edge="end"
            aria-label="clear"
            onClick={handleClearHistory}
            color="error"
          >
            <ClearIcon />
          </IconButton>
        </Box>
      </Box>

      {/* 智能体选择 */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, overflowX: 'auto', pb: 1 }}>
        {agents.map((agent) => (
          <Chip
            key={agent}
            label={`@${agent}`}
            variant="outlined"
            onClick={() => insertAgentMention(agent)}
            sx={{ cursor: 'pointer' }}
          />
        ))}
      </Box>

      {/* 聊天消息列表 */}
      <Paper
        elevation={3}
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          mb: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {messages.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body1" color="text.secondary" align="center">
              开始与智能体对话吧！你可以直接提问，或@特定智能体获取专业帮助
            </Typography>
          </Box>
        ) : (
          <List sx={{ width: '100%', padding: 0 }}>
            {messages.map((message) => {
              const isUser = message.sender_type === 'user';
              return (
                <React.Fragment key={message.id}>
                  <ListItem
                    sx={{
                      justifyContent: isUser ? 'flex-end' : 'flex-start',
                      padding: '8px 0',
                    }}
                  >
                    {!isUser && (
                      <Avatar sx={{ mr: 1, bgcolor: '#1976d2' }}>
                        {message.sender_name.charAt(0)}
                      </Avatar>
                    )}
                    <Paper
                      elevation={1}
                      sx={{
                        maxWidth: '70%',
                        p: 1.5,
                        bgcolor: isUser ? '#e3f2fd' : 'white',
                        borderRadius: isUser ? '16px 4px 16px 16px' : '4px 16px 16px 16px',
                      }}
                    >
                      {!isUser && (
                        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 0.5 }}>
                          {message.sender_name}
                        </Typography>
                      )}
                      <ReactMarkdown
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '');
                            return !inline && match ? (
                              <pre
                                className={className}
                                style={{
                                  backgroundColor: '#f5f5f5',
                                  padding: '8px',
                                  borderRadius: '4px',
                                  overflow: 'auto',
                                  fontSize: '0.85em',
                                }}
                              >
                                <code className={className} {...props}>
                                  {children}
                                </code>
                              </pre>
                            ) : (
                              <code
                                className={className}
                                style={{
                                  backgroundColor: '#f5f5f5',
                                  padding: '2px 4px',
                                  borderRadius: '3px',
                                  fontFamily: 'monospace',
                                }}
                                {...props}
                              >
                                {children}
                              </code>
                            );
                          },
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </Paper>
                    {isUser && (
                      <Avatar sx={{ ml: 1, bgcolor: '#4caf50' }}>
                        U
                      </Avatar>
                    )}
                  </ListItem>
                  <Divider variant="middle" sx={{ opacity: 0.3 }} />
                </React.Fragment>
              );
            })}
            <div ref={messagesEndRef} />
          </List>
        )}
      </Paper>

      {/* 消息输入区域 */}
      <Box sx={{ display: 'flex', gap: 1, alignItems: 'flex-end' }}>
        <TextField
          fullWidth
          multiline
          rows={3}
          variant="outlined"
          placeholder="输入消息... 可以@特定智能体获取专业帮助"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          InputProps={{
            endAdornment: (
              <IconButton
                color="primary"
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                aria-label="send"
              >
                <SendIcon />
              </IconButton>
            ),
          }}
        />
      </Box>

      {/* 通知组件 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbarSeverity}
          variant="filled"
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default ChatInterface;
