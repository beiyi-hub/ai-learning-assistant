import React, { useState, useEffect } from 'react';
import { Button, TextField, Dialog, DialogTitle, DialogContent, DialogActions, List, ListItem, ListItemText, IconButton, Typography, Box, Grid } from '@mui/material';
import { Add as AddIcon, Delete as DeleteIcon, Edit as EditIcon, Visibility as ViewIcon } from '@mui/icons-material';
import { projectApi } from '../../services/api';

const ProjectManager = ({ onSelectProject }) => {
  const [projects, setProjects] = useState([]);
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState(false);
  const [currentProject, setCurrentProject] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    topic: '',
  });

  // 获取项目列表
  const fetchProjects = async () => {
    try {
      const response = await projectApi.getProjects();
      setProjects(response.data);
    } catch (error) {
      console.error('获取项目列表失败:', error);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  // 处理表单输入变化
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  // 打开创建项目对话框
  const handleCreateClick = () => {
    setEditing(false);
    setFormData({ name: '', description: '', topic: '' });
    setOpen(true);
  };

  // 打开编辑项目对话框
  const handleEditClick = (project) => {
    setEditing(true);
    setCurrentProject(project);
    setFormData({
      name: project.name,
      description: project.description,
      topic: project.topic,
    });
    setOpen(true);
  };

  // 关闭对话框
  const handleClose = () => {
    setOpen(false);
    setCurrentProject(null);
  };

  // 提交表单
  const handleSubmit = async () => {
    try {
      if (editing && currentProject) {
        // 更新项目
        await projectApi.updateProject(currentProject.id, formData);
      } else {
        // 创建项目
        await projectApi.createProject(formData);
      }

      // 刷新项目列表
      fetchProjects();
      // 关闭对话框
      handleClose();
    } catch (error) {
      console.error('操作项目失败:', error);
    }
  };

  // 删除项目
  const handleDelete = async (projectId) => {
    try {
      await projectApi.deleteProject(projectId);
      // 刷新项目列表
      fetchProjects();
    } catch (error) {
      console.error('删除项目失败:', error);
    }
  };

  return (
    <Box sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          学习项目
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateClick}
        >
          创建项目
        </Button>
      </Box>

      <List sx={{ flexGrow: 1, overflow: 'auto' }}>
        {projects.length === 0 ? (
          <Typography variant="body1" color="text.secondary" align="center" sx={{ mt: 4 }}>
            暂无项目，点击"创建项目"开始你的学习之旅
          </Typography>
        ) : (
          projects.map((project) => (
            <ListItem
              key={project.id}
              secondaryAction={
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <IconButton
                    edge="end"
                    aria-label="view"
                    onClick={() => onSelectProject(project)}
                  >
                    <ViewIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="edit"
                    onClick={() => handleEditClick(project)}
                  >
                    <EditIcon />
                  </IconButton>
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={() => handleDelete(project.id)}
                    color="error"
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              }>
              <ListItemText
                primary={project.name}
                secondary={
                  <>
                    <Typography
                      component="span"
                      variant="body2"
                      sx={{ display: 'inline' }}
                    >
                      {project.topic}
                    </Typography>
                    <br />
                    {project.description}
                  </>
                }
              />
            </ListItem>
          ))
        )}
      </List>

      {/* 创建/编辑项目对话框 */}
      <Dialog open={open} onClose={handleClose} fullWidth maxWidth="sm">
        <DialogTitle>{editing ? '编辑项目' : '创建项目'}</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                autoFocus
                margin="dense"
                label="项目名称"
                name="name"
                type="text"
                fullWidth
                variant="outlined"
                value={formData.name}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="学习主题"
                name="topic"
                type="text"
                fullWidth
                variant="outlined"
                value={formData.topic}
                onChange={handleInputChange}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                margin="dense"
                label="项目描述"
                name="description"
                type="text"
                fullWidth
                variant="outlined"
                multiline
                rows={3}
                value={formData.description}
                onChange={handleInputChange}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>取消</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editing ? '更新' : '创建'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ProjectManager;
