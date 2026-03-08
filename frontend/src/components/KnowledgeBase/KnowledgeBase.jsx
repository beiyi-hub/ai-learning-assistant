import React, { useState, useEffect } from 'react';
import { Box, TextField, Button, Typography, List, ListItem, ListItemText, IconButton, Paper, Dialog, DialogTitle, DialogContent, DialogActions, Chip, Grid, Divider, Tabs, Tab, InputAdornment } from '@mui/material';
import { Search as SearchIcon, Add as AddIcon, Edit as EditIcon, Delete as DeleteIcon, Info as InfoIcon } from '@mui/icons-material';
import { knowledgeApi } from '../../services/api';
import ReactMarkdown from 'react-markdown';

const KnowledgeBase = ({ selectedProject }) => {
  const [knowledgeItems, setKnowledgeItems] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [currentItem, setCurrentItem] = useState(null);
  const [formData, setFormData] = useState({
    content: '',
    type: 'note',
    tags: [],
  });
  const [summary, setSummary] = useState(null);

  // 获取项目知识库
  const fetchKnowledgeItems = async () => {
    if (!selectedProject) return;
    
    try {
      const response = await knowledgeApi.getProjectKnowledge(selectedProject.id);
      setKnowledgeItems(response.data);
    } catch (error) {
      console.error('获取知识库失败:', error);
    }
  };

  // 获取知识库摘要
  const fetchKnowledgeSummary = async () => {
    if (!selectedProject) return;
    
    try {
      const response = await knowledgeApi.getKnowledgeSummary(selectedProject.id);
      setSummary(response.data);
    } catch (error) {
      console.error('获取知识库摘要失败:', error);
    }
  };

  useEffect(() => {
    fetchKnowledgeItems();
    fetchKnowledgeSummary();
  }, [selectedProject]);

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // 打开创建知识点对话框
  const handleCreateClick = () => {
    setEditing(false);
    setFormData({ content: '', type: 'note', tags: [] });
    setCurrentItem(null);
    setOpen(true);
  };

  // 打开编辑知识点对话框
  const handleEditClick = (item) => {
    setEditing(true);
    setCurrentItem(item);
    setFormData({
      content: item.content,
      type: item.type,
      tags: item.tags.join(','),
    });
    setOpen(true);
  };

  // 关闭对话框
  const handleClose = () => {
    setOpen(false);
    setCurrentItem(null);
  };

  // 提交表单
  const handleSubmit = async () => {
    if (!selectedProject) return;
    
    try {
      // 处理标签
      const tags = formData.tags
        .split(',')
        .map(tag => tag.trim())
        .filter(tag => tag);
      
      // 创建知识点数据
      const itemData = {
        content: formData.content,
        type: formData.type,
        tags: tags,
        project_id: selectedProject.id,
      };
      
      // 添加或更新知识点
      await knowledgeApi.addKnowledgeItem(itemData);
      
      // 刷新知识库
      fetchKnowledgeItems();
      fetchKnowledgeSummary();
      
      // 关闭对话框
      handleClose();
    } catch (error) {
      console.error('操作知识点失败:', error);
    }
  };

  // 删除知识点
  const handleDelete = async (itemId) => {
    try {
      await knowledgeApi.deleteKnowledgeItem(itemId);
      // 刷新知识库
      fetchKnowledgeItems();
      fetchKnowledgeSummary();
    } catch (error) {
      console.error('删除知识点失败:', error);
    }
  };

  // 搜索知识库
  const handleSearch = async () => {
    if (!selectedProject || !searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    
    try {
      setIsSearching(true);
      
      const response = await knowledgeApi.retrieveKnowledge({
        project_id: selectedProject.id,
        query: searchQuery.trim(),
        limit: 10,
      });
      
      setSearchResults(response.data.items);
    } catch (error) {
      console.error('搜索知识库失败:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // 获取知识点类型的显示名称
  const getTypeDisplayName = (type) => {
    const typeMap = {
      note: '笔记',
      concept: '概念',
      confusion: '疑惑点',
      interest: '兴趣点',
    };
    return typeMap[type] || type;
  };

  // 获取知识点类型的颜色
  const getTypeColor = (type) => {
    const colorMap = {
      note: 'default',
      concept: 'primary',
      confusion: 'error',
      interest: 'success',
    };
    return colorMap[type] || 'default';
  };

  // 处理标签输入变化
  const handleTagsChange = (e) => {
    setFormData({ ...formData, tags: e.target.value });
  };

  // 处理标签点击
  const handleTagClick = (tag) => {
    setSearchQuery(tag);
    handleSearch();
    setActiveTab(1); // 切换到搜索标签
  };

  if (!selectedProject) {
    return (
      <Box sx={{ p: 3, height: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <Typography variant="h6" color="text.secondary" align="center">
          请选择一个学习项目查看知识库
        </Typography>
      </Box>
    );
  }

  // 过滤当前标签页的知识点
  const filteredItems = activeTab === 0 
    ? knowledgeItems 
    : searchResults;

  // 根据类型过滤知识点
  const getItemsByType = (type) => {
    return filteredItems.filter(item => item.type === type);
  };

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* 知识库标题和操作 */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h5" component="h2">
          知识库
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateClick}
        >
          添加知识点
        </Button>
      </Box>

      {/* 知识库统计信息 */}
      {summary && (
        <Paper elevation={2} sx={{ p: 2, mb: 2, display: 'flex', gap: 3, flexWrap: 'wrap' }}>
          <Box>
            <Typography variant="body2" color="text.secondary">
              总知识点
            </Typography>
            <Typography variant="h6">{summary.total_items}</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              概念
            </Typography>
            <Typography variant="h6">{summary.concepts}</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              笔记
            </Typography>
            <Typography variant="h6">{summary.notes}</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              疑惑点
            </Typography>
            <Typography variant="h6">{summary.confusions}</Typography>
          </Box>
          <Box>
            <Typography variant="body2" color="text.secondary">
              兴趣点
            </Typography>
            <Typography variant="h6">{summary.interests}</Typography>
          </Box>
        </Paper>
      )}

      {/* 标签页 */}
      <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)} sx={{ mb: 2 }}>
        <Tab label="所有知识点" />
        <Tab label="搜索结果" />
      </Tabs>

      {/* 搜索框 */}
      {activeTab === 1 && (
        <TextField
          fullWidth
          placeholder="搜索知识库..."
          variant="outlined"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          disabled={isSearching}
          sx={{ mb: 2 }}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton
                  color="primary"
                  onClick={handleSearch}
                  disabled={!searchQuery.trim() || isSearching}
                  aria-label="search"
                >
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
      )}

      {/* 知识点列表 */}
      <Paper
        elevation={3}
        sx={{
          flexGrow: 1,
          overflow: 'auto',
          p: 2,
          mb: 2,
        }}
      >
        {filteredItems.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 200 }}>
            <Typography variant="body1" color="text.secondary" align="center">
              {activeTab === 0 ? '知识库为空，点击"添加知识点"开始积累知识' : '没有找到匹配的知识点'}
            </Typography>
          </Box>
        ) : (
          <Box>
            {/* 概念 */}
            {getItemsByType('concept').length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                  <Chip label="概念" color="primary" size="small" sx={{ mr: 1 }} />
                </Typography>
                <List sx={{ width: '100%' }}>
                  {getItemsByType('concept').map((item) => (
                    <ListItem
                      key={item.id}
                      secondaryAction={
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleEditClick(item)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDelete(item.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={<ReactMarkdown>{item.content.split('\n')[0]}</ReactMarkdown>}
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {item.tags.map((tag) => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                sx={{ mr: 0.5, mb: 0.5, cursor: 'pointer' }}
                                onClick={() => handleTagClick(tag)}
                              />
                            ))}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
                <Divider sx={{ mt: 2 }} />
              </Box>
            )}

            {/* 笔记 */}
            {getItemsByType('note').length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                  <Chip label="笔记" color="default" size="small" sx={{ mr: 1 }} />
                </Typography>
                <List sx={{ width: '100%' }}>
                  {getItemsByType('note').map((item) => (
                    <ListItem
                      key={item.id}
                      secondaryAction={
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleEditClick(item)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDelete(item.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={<ReactMarkdown>{item.content.split('\n')[0]}</ReactMarkdown>}
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {item.tags.map((tag) => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                sx={{ mr: 0.5, mb: 0.5, cursor: 'pointer' }}
                                onClick={() => handleTagClick(tag)}
                              />
                            ))}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
                <Divider sx={{ mt: 2 }} />
              </Box>
            )}

            {/* 疑惑点 */}
            {getItemsByType('confusion').length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                  <Chip label="疑惑点" color="error" size="small" sx={{ mr: 1 }} />
                </Typography>
                <List sx={{ width: '100%' }}>
                  {getItemsByType('confusion').map((item) => (
                    <ListItem
                      key={item.id}
                      secondaryAction={
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleEditClick(item)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDelete(item.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={<ReactMarkdown>{item.content.split('\n')[0]}</ReactMarkdown>}
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {item.tags.map((tag) => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                sx={{ mr: 0.5, mb: 0.5, cursor: 'pointer' }}
                                onClick={() => handleTagClick(tag)}
                              />
                            ))}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
                <Divider sx={{ mt: 2 }} />
              </Box>
            )}

            {/* 兴趣点 */}
            {getItemsByType('interest').length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" sx={{ mb: 1, display: 'flex', alignItems: 'center' }}>
                  <Chip label="兴趣点" color="success" size="small" sx={{ mr: 1 }} />
                </Typography>
                <List sx={{ width: '100%' }}>
                  {getItemsByType('interest').map((item) => (
                    <ListItem
                      key={item.id}
                      secondaryAction={
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleEditClick(item)}
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDelete(item.id)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Box>
                      }
                    >
                      <ListItemText
                        primary={<ReactMarkdown>{item.content.split('\n')[0]}</ReactMarkdown>}
                        secondary={
                          <Box sx={{ mt: 0.5 }}>
                            {item.tags.map((tag) => (
                              <Chip
                                key={tag}
                                label={tag}
                                size="small"
                                sx={{ mr: 0.5, mb: 0.5, cursor: 'pointer' }}
                                onClick={() => handleTagClick(tag)}
                              />
                            ))}
                          </Box>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}
          </Box>
        )}
      </Paper>

      {/* 创建/编辑知识点对话框 */}
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="md">
        <DialogTitle>{editing ? '编辑知识点' : '添加知识点'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="知识点类型"
                name="type"
                select
                fullWidth
                variant="outlined"
                value={formData.type}
                onChange={handleInputChange}
                SelectProps={{
                  native: true,
                }}
              >
                <option value="note">笔记</option>
                <option value="concept">概念</option>
                <option value="confusion">疑惑点</option>
                <option value="interest">兴趣点</option>
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="知识点内容"
                name="content"
                multiline
                rows={8}
                fullWidth
                variant="outlined"
                value={formData.content}
                onChange={handleInputChange}
                placeholder="使用Markdown格式编写知识点内容..."
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="标签（用逗号分隔）"
                name="tags"
                type="text"
                fullWidth
                variant="outlined"
                value={formData.tags}
                onChange={handleTagsChange}
                placeholder="机器学习, 深度学习, 神经网络"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>取消</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editing ? '更新' : '添加'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default KnowledgeBase;
