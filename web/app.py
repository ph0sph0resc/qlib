"""
QLib Web Application
Flask application for QLib visualization
"""
import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import config
from config import (
    DATABASE_URI,
    DEBUG,
    HOST,
    PORT,
    MODEL_CATEGORIES,
    ALPHA_FACTORS,
    STRATEGY_TYPES,
    TASK_STATUS,
    TASK_TYPES
)

# Import database models
from api.models import db

# Import API modules
from api.qlib_wrapper import qlib
from api.config_parser import ConfigParser
from api.task_manager import task_manager, TaskStatus
from api import rebalance_api

# Initialize Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')

# Flask configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = DEBUG

# Enable CORS
CORS(app)

# Initialize database
db.init_app(app)


# ============================================================================
# Task Status Sync Helper
# ============================================================================

def update_task_in_db(task):
    """将任务状态同步到数据库"""
    try:
        from api.models import Experiment
        from datetime import timezone, datetime
        import json

        logger.info(f'update_task_in_db called - task.id={task.id}, task.status={task.status}, task.progress={task.progress}')

        with app.app_context():
            experiment = Experiment.query.get(task.id)
            if experiment:
                logger.info(f'Before update - db.status={experiment.status}, db.progress={experiment.progress}')

                experiment.status = task.status
                experiment.progress = task.progress
                experiment.message = task.message

                if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    experiment.completed_at = datetime.now(timezone.utc)
                    logger.info(f'Setting completed_at to {experiment.completed_at}')
                    if task.result:
                        experiment.results = json.dumps(task.result, default=str)
                        logger.info(f'Saved results')
                    if task.error:
                        experiment.error = task.error
                        logger.info(f'Saved error')

                db.session.commit()
                logger.info(f'After update - db.status={experiment.status}, db.progress={experiment.progress}, db.completed_at={experiment.completed_at}')
            else:
                logger.warning(f'Experiment {task.id} not found in database')
    except Exception as e:
        logger.error(f'Failed to sync task to database: {e}', exc_info=True)


# ============================================================================
# Routes - Pages
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/factor_test')
def factor_test():
    """Factor test page"""
    return render_template('factor_test.html')


@app.route('/model_train')
def model_train():
    """Model training page"""
    return render_template('model_train.html')


@app.route('/backtest')
def backtest():
    """Backtest page"""
    return render_template('backtest.html')


@app.route('/analysis')
def analysis():
    """Analysis page"""
    return render_template('analysis.html')

@app.route('/rebalance_analysis')
def rebalance_analysis():
    """Rebalance analysis page"""
    return render_template('rebalance_analysis.html')


# ============================================================================
# API Routes - System
# ============================================================================

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'status': 'ok',
        'version': '0.1.0',
        'tasks_running': task_manager.get_running_count(),
        'max_concurrent_tasks': task_manager.max_concurrent_tasks
    })


@app.route('/api/examples')
def api_examples():
    """Get all available examples"""
    examples = qlib.list_examples()
    return jsonify(examples)


@app.route('/api/examples/<category>/<path:config_path>')
def api_example_config(category, config_path):
    """Get specific example configuration"""
    full_path = f'{category}/{config_path}'
    config = qlib.get_example_config(full_path)

    if config:
        return jsonify({'success': True, 'config': config})
    return jsonify({'success': False, 'error': 'Configuration not found'}), 404


@app.route('/api/models')
def api_models():
    """Get available models"""
    return jsonify(MODEL_CATEGORIES)


@app.route('/api/markets')
def api_markets():
    """Get available markets"""
    return jsonify({
        'markets': ['csi300', 'csi500', 'all'],
        'alphas': ALPHA_FACTORS,
        'strategies': STRATEGY_TYPES
    })


# ============================================================================
# API Routes - Configuration
# ============================================================================

@app.route('/api/config/template/<category>/<path:template_name>', methods=['GET'])
def api_config_template(category, template_name):
    """Get YAML configuration template"""
    full_path = f'{category}/{template_name}'
    config = qlib.get_example_config(full_path)

    if config:
        schema = ConfigParser.yaml_to_form_schema(config)
        return jsonify({
            'success': True,
            'config': config,
            'schema': schema
        })
    return jsonify({'success': False, 'error': 'Template not found'}), 404


@app.route('/api/config/schema/<model_name>')
def api_config_schema(model_name):
    """Get parameter schema for a model"""
    schema = ConfigParser.get_model_schema(model_name)
    return jsonify(schema)


@app.route('/api/config/validate', methods=['POST'])
def api_config_validate():
    """Validate YAML configuration"""
    try:
        data = request.get_json()
        yaml_content = data.get('yaml', '')

        config = ConfigParser.parse_yaml_string(yaml_content)
        if config is None:
            return jsonify({'success': False, 'error': 'Invalid YAML'})

        is_valid, errors = ConfigParser.validate_config(config)

        if is_valid:
            return jsonify({'success': True, 'valid': True})
        else:
            return jsonify({'success': True, 'valid': False, 'errors': errors})

    except Exception as e:
        logger.error(f'Config validation error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/config/generate', methods=['POST'])
def api_config_generate():
    """Generate YAML from form data"""
    try:
        data = request.get_json()
        form_data = data.get('form_data', {})
        template_name = data.get('template_name')

        template_config = None
        if template_name:
            template_config = qlib.get_example_config(template_name)

        yaml_content = ConfigParser.form_to_yaml(form_data, template_config)

        return jsonify({'success': True, 'yaml': yaml_content})

    except Exception as e:
        logger.error(f'Config generation error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# API Routes - Tasks
# ============================================================================

@app.route('/api/task', methods=['POST'])
def api_task_create():
    """Create a new task"""
    try:
        data = request.get_json()
        task_type = data.get('task_type')
        config = data.get('config', {})
        name = data.get('name', 'Unnamed Task')
        logger.info(['config={config}'])
        # Determine which function to call
        if task_type == TASK_TYPES['FACTOR_TEST']:
            func = qlib.run_factor_analysis
        elif task_type == TASK_TYPES['MODEL_TRAIN']:
            func = qlib.train_model
        elif task_type == TASK_TYPES['BACKTEST']:
            func = qlib.run_backtest
        else:
            return jsonify({'success': False, 'error': 'Invalid task type'}), 400

        # Create task
        task_id = task_manager.create_task(task_type, func, kwargs={'config': config})

        # 获取任务并注册状态同步回调
        task = task_manager.get_task(task_id)
        if task:
            task.add_status_callback(update_task_in_db)

        # Store in database
        with app.app_context():
            from api.models import Experiment
            import uuid

            experiment = Experiment(
                id=task_id,
                name=name,
                task_type=task_type,
                status=TASK_STATUS['PENDING'],
                config=ConfigParser.yaml_to_string(config)
            )
            db.session.add(experiment)
            db.session.commit()

        return jsonify({'success': True, 'task_id': task_id})

    except Exception as e:
        logger.error(f'Task creation error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400




@app.route('/api/task/<task_id>/start', methods=['POST'])
def api_task_start(task_id):
    """Start a task"""
    if task_manager.start_task(task_id):
        # Update database
        with app.app_context():
            from api.models import Experiment
            from datetime import datetime, timezone

            experiment = Experiment.query.get(task_id)
            if experiment:
                experiment.status = TASK_STATUS['RUNNING']
                experiment.started_at = datetime.now(timezone.utc)
                db.session.commit()

        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task not found or cannot start'}), 404


@app.route('/api/task/<task_id>/stop', methods=['POST'])
def api_task_stop(task_id):
    """Stop a task"""
    if task_manager.stop_task(task_id):
        # Update database
        with app.app_context():
            from api.models import Experiment

            experiment = Experiment.query.get(task_id)
            if experiment:
                experiment.status = TaskStatus.CANCELLED
                db.session.commit()

        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Task not found'}), 404


@app.route('/api/task/<task_id>/status')
def api_task_status(task_id):
    """Get task status"""
    task = task_manager.get_task(task_id)
    if task:
        return jsonify({'success': True, 'task': task.to_dict()})
    return jsonify({'success': False, 'error': 'Task not found'}), 404


@app.route('/api/task/<task_id>/log')
def api_task_log(task_id):
    """Get task logs"""
    logs = task_manager.get_task_logs(task_id)
    return jsonify({'success': True, 'logs': logs})


@app.route('/api/tasks')
def api_tasks_list():
    """List all tasks"""
    filters = {}

    status = request.args.get('status')
    if status:
        filters['status'] = status

    task_type = request.args.get('type')
    if task_type:
        filters['type'] = task_type

    tasks = task_manager.list_tasks(filters)
    return jsonify({'success': True, 'tasks': tasks})


# ============================================================================
# API Routes - Analysis
# ============================================================================

@app.route('/api/analysis/list')
def api_analysis_list():
    """Get all experiment records"""
    try:
        from api.models import Experiment

        page = int(request.args.get('page', 1))
        page_size = min(int(request.args.get('page_size', 20)), 100)

        status = request.args.get('status')
        task_type = request.args.get('task_type')

        logger.info(f'API /api/analysis/list - params: status={status}, task_type={task_type}')

        query = Experiment.query

        if status:
            query = query.filter_by(status=status)
        if task_type:
            query = query.filter_by(task_type=task_type)

        query = query.order_by(Experiment.created_at.desc())

        pagination = query.paginate(page=page, per_page=page_size, error_out=False)

        logger.info(f'API /api/analysis/list - found {pagination.total} experiments, returning {len(pagination.items)} items')

        return jsonify({
            'success': True,
            'experiments': [e.to_dict() for e in pagination.items],
            'total': pagination.total,
            'page': page,
            'pages': pagination.pages
        })

    except Exception as e:
        logger.error(f'Analysis list error: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/analysis/detail/<experiment_id>')
def api_analysis_detail(experiment_id):
    """Get experiment detail"""
    try:
        from api.models import Experiment

        experiment = Experiment.query.get(experiment_id)
        if experiment:
            return jsonify({'success': True, 'experiment': experiment.to_dict()})

        return jsonify({'success': False, 'error': 'Experiment not found'}), 404

    except Exception as e:
        logger.error(f'Analysis detail error: {e}')
        return jsonify({'success': False, 'error': str(e)}), 400


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error: {error}')
    return jsonify({'success': False, 'error': 'Internal server error'}), 500





# ============================================================================
# API Routes - Rebalance
# ============================================================================
@app.route('/api/rebalance/history')
def api_rebalance_history():
    """Get rebalance history for a backtest task"""
    logger.info(f'api_rebalance_history called with task_id={request.args.get("task_id")}')
    return jsonify(rebalance_api.get_rebalance_history(request.args.get('task_id')))




@app.route('/api/rebalance/summary')
def api_rebalance_summary():
    """Get rebalance summary for a backtest task"""
    task_id = request.args.get('task_id')
    history_response = rebalance_api.get_rebalance_history(task_id)
    return jsonify({
        'success': history_response.get('success'),
        'summary': history_response.get('summary', {})
    })


@app.route('/api/rebalance/export')
def api_rebalance_export():
    """Export rebalance history as CSV or Excel"""
    try:
        import io
        task_id = request.args.get('task_id')
        export_format = request.args.get('format', 'csv')

        if not task_id:
            return jsonify({'success': False, 'error': 'task_id parameter required'}), 400

        result = rebalance_api.export_rebalance_history(task_id, export_format)
        if result:
            data, filename, mimetype = result
            return send_file(
                io.BytesIO(data.encode('utf-8')),
                mimetype=mimetype,
                as_attachment=True,
                download_name=filename
            )

        return jsonify({'success': False, 'error': 'Failed to export rebalance history'}), 400

    except Exception as e:
        logger.error(f'Rebalance export error: {e}', exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 400

# ============================================================================
# Main
# ============================================================================

def create_app():
    """Create and configure Flask application"""
    # Create database tables
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    logger.info(f'Starting QLib Web on {HOST}:{PORT}')
    app.run(host=HOST, port=PORT, debug=DEBUG)
