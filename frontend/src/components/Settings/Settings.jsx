import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, TextField, Button, Divider, Switch, FormControlLabel, Grid, Alert, Snackbar } from '@mui/material';
import { settingsApi } from '../../services/api';

const Settings = () => {
  const [settings, setSettings] = useState({
    model_settings: {
      provider: 'openai',
      api_key: '',
      base_url: '',
      model_name: 'gpt-3.5-turbo',
      temperature: 0.3,
      max_tokens: 1000,
      top_p: 1.0,
      frequency_penalty: 0.0,
      presence_penalty: 0.0
    }
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [showApiKey, setShowApiKey] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState('success');

  // 获取当前设置
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const response = await settingsApi.getSettings();
        setSettings(response.data);
      } catch (error) {
        console.error('获取设置失败:', error);
        setSnackbarMessage('获取设置失败');
        setSnackbarSeverity('error');
        setSnackbarOpen(true);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  // 处理设置变化
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    
    // 解析数字值
    const processedValue = type === 'number' ? parseFloat(value) || 0 : value;
    
    // 更新设置
    setSettings(prevSettings => ({
      ...prevSettings,
      model_settings: {
        ...prevSettings.model_settings,
        [name]: type === 'checkbox' ? checked : processedValue
      }
    }));
  };

  // 保存设置
  const handleSave = async () => {
    try {
      setSaving(true);
      await settingsApi.updateSettings(settings);
      setSnackbarMessage('设置保存成功');
      setSnackbarSeverity('success');
      setSnackbarOpen(true);
    } catch (error) {
      console.error('保存设置失败:', error);
      setSnackbarMessage('保存设置失败');
      setSnackbarSeverity('error');
      setSnackbarOpen(true);
    } finally {
      setSaving(false);
    }
  };

  // 关闭提示
  const handleCloseSnackbar = () => {
    setSnackbarOpen(false);
  };

  if (loading) {
    return (
      <Box sx={{ p: 2 }}>
        <Typography variant="body1">加载设置中...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h5" component="h2" sx={{ mb: 3 }}>
        系统设置
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          大模型API设置
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={2}>
          {/* 模型提供商 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="模型提供商"
              name="provider"
              value={settings.model_settings.provider}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>

          {/* API密钥 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="API密钥"
              name="api_key"
              type={showApiKey ? 'text' : 'password'}
              value={settings.model_settings.api_key}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="输入您的大模型API密钥"
            />
          </Grid>

          {/* 显示API密钥开关 */}
          <Grid item xs={12}>
            <FormControlLabel
              control={<Switch checked={showApiKey} onChange={() => setShowApiKey(!showApiKey)} />}
              label="显示API密钥"
            />
          </Grid>

          {/* API基础URL */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="API基础URL（可选）"
              name="base_url"
              value={settings.model_settings.base_url}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="如果使用自定义API服务，请输入完整的基础URL"
            />
          </Grid>

          {/* 模型名称 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="模型名称"
              name="model_name"
              value={settings.model_settings.model_name}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
            />
          </Grid>

          {/* 温度参数 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="温度参数"
              name="temperature"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={settings.model_settings.temperature}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="控制输出的随机性，值越大越随机"
            />
          </Grid>

          {/* 最大令牌数 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="最大令牌数"
              name="max_tokens"
              type="number"
              step="1"
              min="1"
              max="4096"
              value={settings.model_settings.max_tokens}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="控制响应的最大长度"
            />
          </Grid>

          {/* Top P参数 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Top P参数"
              name="top_p"
              type="number"
              step="0.1"
              min="0"
              max="1"
              value={settings.model_settings.top_p}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="控制采样范围，值越小越集中"
            />
          </Grid>

          {/* 频率惩罚 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="频率惩罚"
              name="frequency_penalty"
              type="number"
              step="0.1"
              min="-2"
              max="2"
              value={settings.model_settings.frequency_penalty}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="减少重复词汇的出现"
            />
          </Grid>

          {/* 存在惩罚 */}
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="存在惩罚"
              name="presence_penalty"
              type="number"
              step="0.1"
              min="-2"
              max="2"
              value={settings.model_settings.presence_penalty}
              onChange={handleChange}
              variant="outlined"
              sx={{ mb: 2 }}
              helperText="增加新主题的出现概率"
            />
          </Grid>
        </Grid>
      </Paper>

      {/* 保存按钮 */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          onClick={handleSave}
          disabled={saving}
          size="large"
        >
          {saving ? '保存中...' : '保存设置'}
        </Button>
      </Box>

      {/* 提示信息 */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={handleCloseSnackbar}
          severity={snackbarSeverity}
          sx={{ width: '100%' }}
        >
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
