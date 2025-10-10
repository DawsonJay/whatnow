import { Activity } from '../types';

interface ActivityCardProps {
  activity: Activity;
  onChoose: () => void;
}

export default function ActivityCard({ activity, onChoose }: ActivityCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 flex flex-col items-center justify-center min-h-[300px] hover:shadow-3xl transition-shadow duration-300">
      <h3 className="text-3xl font-semibold text-gray-800 mb-8 text-center">
        {activity.name}
      </h3>
      <button
        onClick={onChoose}
        className="px-8 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-lg font-medium rounded-lg hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-xl transition-all duration-200 transform hover:-translate-y-1"
      >
        Choose This
      </button>
    </div>
  );
}



